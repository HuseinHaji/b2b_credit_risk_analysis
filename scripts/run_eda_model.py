import pandas as pd
import matplotlib
matplotlib.use('Agg')
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, roc_auc_score
from sqlalchemy import create_engine
import joblib

if __name__ == '__main__':
    engine = create_engine('postgresql://huseyn@localhost:5432/b2b_credit_risk')

    fact_exposure = pd.read_sql('SELECT * FROM credit_risk_dw.fact_exposure_snapshot', engine)
    fact_default = pd.read_sql('SELECT * FROM credit_risk_dw.fact_default_event', engine)
    dim_customer = pd.read_sql('SELECT * FROM credit_risk_dw.dim_customer', engine)

    print('fact_exposure', fact_exposure.shape)
    print('fact_default', fact_default.shape)
    print('dim_customer', dim_customer.shape)

    print(fact_exposure[['current_exposure','overdue_exposure','utilization_ratio']].describe())

    features = fact_exposure.groupby('customer_key').agg(
        current_exposure=('current_exposure','mean'),
        overdue_exposure=('overdue_exposure','mean'),
        utilization_ratio=('utilization_ratio','mean'),
        avg_sales=('monthly_sales_estimate','mean'),
        invoice_count=('invoice_count_month','mean'),
        rating_key=('rating_key','max'),
    ).reset_index()

    labels = fact_default.groupby('customer_key').size().reset_index(name='has_default')
    labels['has_default'] = (labels['has_default'] > 0).astype(int)

    data = features.merge(labels, on='customer_key', how='left').fillna(0)
    data['has_default'] = data['has_default'].astype(int)

    X = data[['current_exposure','overdue_exposure','utilization_ratio','avg_sales','invoice_count','rating_key']]
    y = data['has_default']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42, stratify=y)

    model = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42, n_jobs=-1)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    y_proba = model.predict_proba(X_test)[:,1]

    print(classification_report(y_test, y_pred))
    print('ROC AUC:', roc_auc_score(y_test, y_proba))

    joblib.dump(model, 'models/eda_rf_default_model.pkl')
    print('Saved model to models/eda_rf_default_model.pkl')

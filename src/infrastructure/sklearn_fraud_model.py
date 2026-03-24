"""
Adapter: SklearnFraudModel.
Implements FraudModelPort using a joblib-serialized scikit-learn model.
"""
from domain.ports.fraud_model_port import FraudModelPort


class SklearnFraudModel(FraudModelPort):

    def __init__(self, model_path: str):
        import joblib
        # Load model once at instantiation (supports Lambda warm start pattern).
        self._model = joblib.load(model_path)

    def predict(self, amount: float, hour: int) -> float:
        import pandas as pd
        # Build input using the same feature schema as training.
        input_data = pd.DataFrame([[amount, hour]], columns=["monto", "hora"])
        # predict_proba returns [normal_probability, fraud_probability].
        return float(self._model.predict_proba(input_data)[0][1])

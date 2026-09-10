import joblib
import onnxmltools
from onnxmltools.convert.common.data_types import FloatTensorType

def convert_model():
    print("Loading XGBoost.pkl...")
    model = joblib.load('XGBoost.pkl')
    
    # onnxmltools expects feature names to be f0, f1, f2, etc. 
    # By setting feature_names to None, we force xgboost to use defaults in its dump.
    model.get_booster().feature_names = None
    
    # We had 7 features used in training (since we dropped TransactionID and isFraud)
    # Let's count them: TransactionAmt, card1, P_emaildomain_freq, card4_freq, ProductCD_freq, amt_z_score_card1, card_tx_count_24h
    # Yes, 7 features.
    
    initial_types = [('float_input', FloatTensorType([None, 7]))]
    
    print("Converting to ONNX...")
    onnx_model = onnxmltools.convert_xgboost(model, initial_types=initial_types)
    
    onnxmltools.utils.save_model(onnx_model, "XGBoost.onnx")
    print("Successfully saved XGBoost.onnx")

if __name__ == "__main__":
    convert_model()

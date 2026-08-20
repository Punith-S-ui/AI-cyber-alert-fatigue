from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.user import User
from app.core.dependencies import require_admin, get_current_user
from app.ml.severity_model import severity_model_service
from app.ml.training_data import generate_training_dataframe

router = APIRouter(prefix="/api/ml", tags=["ml"])


@router.get("/model-info")
def model_info(user: User = Depends(get_current_user)):
    return {
        "severity_model": {
            "algorithm": "RandomForestClassifier",
            "trained": severity_model_service.is_trained(),
            "classes": ["LOW", "MEDIUM", "HIGH", "CRITICAL"],
        },
        "clustering_model": {"algorithm": "TF-IDF + KMeans"},
        "anomaly_model": {"algorithm": "IsolationForest"},
    }


@router.post("/train")
def train_model(db: Session = Depends(get_db), user: User = Depends(require_admin)):
    df = generate_training_dataframe()
    result = severity_model_service.train(df)
    return {"message": "Random Forest severity model trained and saved to disk.", **result}

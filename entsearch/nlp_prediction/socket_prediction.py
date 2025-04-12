import logging
from typing import List, Optional, Tuple
import time
from entsearch import socketio, entity_repo, dataset_repo
from flask_socketio import emit
from .models.pure_entsearch import NameProbabilityAnalyzer

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class DatasetDTO:
    def __init__(self, dataset_name: str, names: List[str], descriptions: List[str]):
        self.dataset_name = dataset_name
        self.names = names
        self.descriptions = descriptions

    def __repr__(self):
        return (
            f"DatasetDTO(dataset_name='{self.dataset_name}', "
            f"names_count={len(self.names)}, "
            f"descriptions_count={len(self.descriptions)})"
        )


def debug_entity_data(entities: List) -> dict:
    """Debug information about entities"""
    if not entities:
        return {"count": 0, "sample_names": [], "sample_descriptions": []}

    return {
        "count": len(entities),
        "sample_names": [e.entity_name for e in entities[:3]],
        "sample_descriptions": [e.description for e in entities[:3]],
        "null_names": sum(1 for e in entities if not e.entity_name),
        "null_descriptions": sum(1 for e in entities if not e.description),
    }


def get_dataset_data(repo, ds_uuid: str) -> DatasetDTO:
    """Fetch dataset data with debug logging"""
    try:
        dataset = dataset_repo.get_ds_by_uuid(ds_uuid)
        if not dataset:
            logger.error(f"Dataset not found for UUID: {ds_uuid}")
            return DatasetDTO("", [], [])

        entities = entity_repo.get_entities_by_dataset_id(dataset.id)
        logger.debug(f"Entity debug data: {debug_entity_data(entities)}")

        if not entities:
            logger.warning(f"No entities found for dataset ID: {dataset.id}")
        print("[DEBUG] dataset model: ", dataset)
        return DatasetDTO(
            dataset_name=dataset.title,
            names=[e.entity_name for e in entities if e.entity_name],
            descriptions=[e.description for e in entities if e.description],
        )
    except Exception as e:
        logger.error(f"Error in get_dataset_data: {str(e)}", exc_info=True)
        return DatasetDTO("", [], [])


def validate_probabilities(names: List[str], probabilities: List[float]) -> bool:
    """Check if probabilities align with names"""
    if len(names) != len(probabilities):
        logger.error(
            f"Length mismatch: names({len(names)}) != probabilities({len(probabilities)})"
        )
        return False
    return True


def get_probabilities(text: str, names: List[str]) -> Optional[List[float]]:
    """Get probabilities with validation"""
    if not names:
        logger.warning("Empty names list provided to get_probabilities")
        return None

    try:
        analyzer = NameProbabilityAnalyzer(names, sensitivity=0.75)
        probabilities = analyzer.calculate_probabilities(text)

        if not validate_probabilities(names, probabilities):
            return None

        logger.info(
            f"Probability stats - max: {max(probabilities):.2f}, "
            f"min: {min(probabilities):.2f}, "
            f"mean: {sum(probabilities)/len(probabilities):.2f}"
        )
        return probabilities
    except Exception as e:
        logger.error(f"Error in get_probabilities: {str(e)}", exc_info=True)
        return None


def filter_by_threshold(
    names: List[str],
    descriptions: List[str],
    probabilities: List[float],
    threshold: float = 0,
    by_description: bool = True,
) -> Tuple[DatasetDTO, List[float], List[int]]:
    """Filter data with comprehensive logging"""
    if not probabilities:
        logger.warning("Empty probabilities list in filter_by_threshold")
        return DatasetDTO("", [], []), [], []

    filtered_indices = [i for i, prob in enumerate(probabilities) if prob >= threshold]
    logger.debug(f"Filtered {len(filtered_indices)} items at threshold {threshold}")

    result = DatasetDTO(
        dataset_name="",
        names=[names[i] for i in filtered_indices if i < len(names)],
        descriptions=[
            descriptions[i]
            for i in filtered_indices
            if by_description and i < len(descriptions)
        ],
    )

    filtered_probs = [probabilities[i] for i in filtered_indices]

    logger.debug(
        f"Filter result - names: {len(result.names)}, "
        f"descriptions: {len(result.descriptions)}, "
        f"probabilities: {len(filtered_probs)}"
    )

    return result, filtered_probs, filtered_indices


@socketio.on("predict")
def handle_prediction(data: dict) -> None:
    """Main prediction handler with enhanced debugging"""
    try:
        emit("clean")
        start_time = time.time()

        logger.debug(f"Received prediction data: {data}")

        dataset_uuids = list(data.get("dataset", []))
        input_text = data.get("text", "")
        threshold = float(data.get("threshold", 0))
        by_description = bool(data.get("isdescription", True))

        logger.info(
            f"Starting prediction for {len(dataset_uuids)} datasets, "
            f"threshold: {threshold}, text length: {len(input_text)}"
        )

        for ds_uuid in dataset_uuids:
            logger.info(f"Processing dataset UUID: {ds_uuid}")
            dataset = get_dataset_data(entity_repo, ds_uuid)
            print(dataset)
            if not dataset.names:
                logger.warning(f"Empty names list for dataset: {ds_uuid}")
                continue

            probabilities = get_probabilities(input_text, dataset.names)
            if not probabilities:
                logger.warning(
                    f"Skipping dataset due to probability calculation error: {ds_uuid}"
                )
                continue

            result, filtered_probs, indices = filter_by_threshold(
                names=dataset.names,
                descriptions=dataset.descriptions,
                probabilities=probabilities,
                threshold=threshold,
                by_description=by_description,
            )

            response = {
                "dataset_name": dataset.dataset_name,
                "amount": len(indices),
                "status": 200,
                "prediction": {
                    "shure": filtered_probs,
                    "id": indices,
                    "name": result.names,
                    "description": result.descriptions,
                },
            }

            logger.debug(f"Response data: {response}")
            emit("data_ready", response)
            time.sleep(0.1)

        logger.info(f"Prediction completed in {time.time() - start_time:.2f}s")

    except Exception as e:
        logger.error(f"Prediction failed: {str(e)}", exc_info=True)
        emit("error", str(e))

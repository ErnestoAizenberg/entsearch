import logging
import time
from typing import List

from flask_socketio import emit

from entsearch import dataset_repo, entity_repo, socketio

from .models.pure_entsearch import NameProbabilityAnalyzer

# Настройка логгирования
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class DatasetDTO:
    def __init__(self, dataset_name: str, names: List[str], descriptions: List[str]):
        self.dataset_name = dataset_name
        self.names = names
        self.descriptions = descriptions


def get_dataset_data(entity_repo, ds_uuid):
    dataset_model = dataset_repo.get_ds_by_uuid(ds_uuid)

    entities = entity_repo.get_entities_by_dataset_id(dataset_model.id)

    # Извлечение имен и описаний из entities
    lst_names = [entity.entity_name for entity in entities]
    lst_descriptions = [entity.description for entity in entities]

    return DatasetDTO(
        names=lst_names, descriptions=lst_descriptions, dataset_name=dataset_model.title
    )


def get_probs(text: str, names: List[str]) -> List[float]:
    logger.info(f'Calculating probabilities for text: "{text}" with names: {names}')
    analyzer = NameProbabilityAnalyzer(names, sensitivity=0.75)
    probs = analyzer.calculate_probabilities(text)
    logger.info(f"Probabilities calculated: {probs}")
    return probs


def filter_by_threshold(
    names: List[str],
    descriptions: List[str],
    list_probs: List[float],
    threshold: float = 0,
    by_description: bool = True,
) -> DatasetDTO:
    logger.info("Filtering data by threshold...")
    filtered_indices = [i for i, prob in enumerate(list_probs) if prob >= threshold]

    filtered_names = [names[i] for i in filtered_indices if i < len(names)]
    filtered_probs = [list_probs[i] for i in filtered_indices]

    if by_description:
        filtered_descriptions = [
            descriptions[i] for i in filtered_indices if i < len(descriptions)
        ]
    else:
        filtered_descriptions = []

    dataset_dto = DatasetDTO(
        names=filtered_names, descriptions=filtered_descriptions, dataset_name=""
    )

    return dataset_dto, filtered_probs, filtered_indices


@socketio.on("predict")
def handle_prediction(data):
    logger.info("Received prediction request...")
    try:
        emit("clean")
        dataset_uuids = list(data["dataset"])
        input_text = data["text"]
        threshold = float(data["threshold"])
        by_description = bool(data["isdescription"])

        for ds_uuid in dataset_uuids:
            logger.info(f"Processing dataset uuid: {ds_uuid}")
            dataset_dto = get_dataset_data(entity_repo, ds_uuid)

            # Получаем вероятности
            lst_probs = get_probs(
                text=input_text,
                names=dataset_dto.names,
            )

            # Фильтруем данные по порогу
            returning_dataset_dto, filtered_probs, filtered_indices = (
                filter_by_threshold(
                    names=dataset_dto.names,
                    descriptions=dataset_dto.descriptions,
                    list_probs=lst_probs,
                    threshold=threshold,
                    by_description=by_description,
                )
            )

            # Формируем ответ
            response_data = {
                "dataset_name": dataset_dto.dataset_name,
                "amount": len(filtered_indices),
                "status": 200,
                "prediction": {
                    "shure": filtered_probs,
                    "id": filtered_indices,
                    "name": returning_dataset_dto.names,
                    "description": returning_dataset_dto.descriptions,
                },
            }

            logger.info(
                f"Response data prepared for dataset id {ds_uuid}: {response_data}"
            )
            emit("data_ready", response_data)
            time.sleep(0.1)  # Небольшая задержка между отправками

    except Exception as e:
        logger.error(
            f"Error occurred while processing prediction request: {e}", exc_info=True
        )
        emit("error", str(e))

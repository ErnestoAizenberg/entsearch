//navbar
function toggleNavbar() { 
    const navbar = document.getElementById('navbar'); 
    if (navbar) {
        navbar.classList.toggle('active'); 
    }
}

// home page
function updateLink() {
    const linkElement = document.getElementById('current_dataset_link');
    const selectedOptions = document.querySelectorAll('#dataset-select option:checked');

    if (linkElement) {
        if (selectedOptions.length > 0) {
            const lastSelectedOption = selectedOptions[selectedOptions.length - 1];
            const lastLink = lastSelectedOption.value;

            linkElement.href = `/current/${lastLink}`;
            linkElement.textContent = `current/${lastLink}`;  
        } else {
            linkElement.href = '/current/'; 
            linkElement.textContent = 'Current'; 
        }
    }
}

const socket = io('http://127.0.0.1:5000');

const predictForm = document.getElementById('predict-form');
if (predictForm) {
    predictForm.onsubmit = function(event) {
        event.preventDefault();
        const threshold = document.getElementById('confidenceThreshold').value / 100;
        const fullness = document.getElementById('precisionRecall').value / 100;
        const istext = document.getElementById('checkbox1')?.checked;
        const isdescription = document.getElementById('checkbox2')?.checked;

        const selectElement = document.getElementById('dataset-select');
        const dataset = Array.from(selectElement.selectedOptions).map(option => option.value);
        const text = this.text.value;

        socket.emit('predict', { dataset, text, threshold, fullness, istext, isdescription });
    };

        socket.on('clean', function() {
            console.log('cleaning of data');          document.getElementById('result').innerHTML = '';
        });

    socket.on('data_ready', (data) => {
        console.log('Received data:', data);
        displayResults(data);
    });

    function displayResults(data) {
        const resultDiv = document.getElementById('result');
        if (resultDiv) {
            resultDiv.innerHTML += `
     <div class="pred-div">
         <div class="prefix"><span style="font-size: 16px; color: #fff5aa;"> ${data.amount}</span><span style="color: #f6ffd5;"> entity was found in: &nbsp;</span><span style="font-size: 18px;">${data.dataset_name}</span></div>
                <div class='tab_of_predicts'>
                    <table class="transparent-table">
                        <thead>
                            <tr><th>ID</th><th>Shure</th><th>Name</th></tr>
                        </thead>
                        <tbody>
                            ${data.prediction.id.map((id, index) => `
                                <tr>
                                    <td>${id}</td>
                                    <td>${data.prediction.shure[index]}</td>
                                    <td>${data.prediction.name[index]}</td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </div></div>
            `;
        }
    }

    // Обновление значений при изменении ползунков
    const confidenceSlider = document.getElementById('confidenceThreshold');
    const precisionSlider = document.getElementById('precisionRecall');
    const confidenceValueDisplay = document.getElementById('confidenceValue');
    const precisionValueDisplay = document.getElementById('precisionValue');

    if (confidenceSlider && confidenceValueDisplay) {
        function updateConfidenceValue() {
            confidenceValueDisplay.textContent = (confidenceSlider.value / 100).toFixed(2);
        }

        confidenceSlider.addEventListener('input', updateConfidenceValue);
        updateConfidenceValue(); // Инициализация значений при загрузке
    }

    if (precisionSlider && precisionValueDisplay) {
        function updatePrecisionValue() {
            precisionValueDisplay.textContent = (precisionSlider.value / 100).toFixed(2);
        }

        precisionSlider.addEventListener('input', updatePrecisionValue);
        updatePrecisionValue(); // Инициализация значений при загрузке
    }

    // Обработка событий на значках вопроса
    document.querySelectorAll('.whatitis').forEach(icon => {
        icon.addEventListener('click', () => {
            const info = icon.nextElementSibling;
            if (info) {
                info.style.display = info.style.display === "block" ? "none" : "block";
            }
        });
    });
}

// csv file 
const csvFileInput = document.getElementById('csv-file');
if (csvFileInput) {
    csvFileInput.addEventListener('change', function(event) {
        event.preventDefault();
    });
}

// Handle dropdowns
const dropdowns = document.querySelectorAll('.dropdown');
dropdowns.forEach(dropdown => {
    const button = dropdown.querySelector('.setting_button');
    const dropdownContent = dropdown.querySelector('.dropdown-content');

    if (button) {
        button.addEventListener('click', (event) => {
            dropdown.classList.toggle('show');
            event.stopPropagation();
        });
    }

    document.addEventListener('click', () => {
        dropdown.classList.remove('show');
    });

    if (dropdownContent) {
        dropdownContent.addEventListener('click', (event) => {
            event.stopPropagation();
        });

        const okButton = dropdown.querySelector('.btn-ok');
        if (okButton) {
            okButton.addEventListener('click', () => {
                dropdown.classList.remove('show');
            });
        }
    }
});

function toggleIdInput() {
    const checkbox = document.getElementById("isid_checkbox");
    const idInputWrapper = document.getElementById("idInputWrapper");
    const nameInput = document.getElementById("name_p");
    const descriptionInput = document.getElementById("description_p");

    if (checkbox && idInputWrapper) {
        if (checkbox.checked) {
            idInputWrapper.style.display = "block";
            nameInput.value = 1;
            nameInput.placeholder = "e.g. 1";
            descriptionInput.value = 2;
            descriptionInput.placeholder = "e.g. 2";
        } else {
            idInputWrapper.style.display = "none";
            nameInput.value = 0;
            nameInput.placeholder = "e.g. 0";
            descriptionInput.value = 1;
            descriptionInput.placeholder = "e.g. 1";
        }
    }
}

// edit_dataset_page
document.addEventListener('DOMContentLoaded', function () {
    const editMenus = document.querySelectorAll('.edit-menu');
    const hiddenIdInput = document.getElementById('hidden-id');
    const wordInput = document.getElementById('word');
    const descriptionTextarea = document.getElementById('description');

    editMenus.forEach(menu => {
        menu.addEventListener('click', function () {
            const entityId = this.getAttribute('data-entityid');
            const entityName = this.getAttribute('data-entityname');
            const description = this.getAttribute('data-description');

            if (hiddenIdInput && wordInput && descriptionTextarea) {
                hiddenIdInput.value = entityId;
                wordInput.value = entityName;
                descriptionTextarea.value = description;
            }
        });
    });
});

function validateWordInput(input) {
    const validWords = /^[a-zA-Zа-яА-ЯёЁ0-9]+$/; 
    if (validWords.test(input.value)) {
        input.classList.add('valid');
    } else {
        input.classList.remove('valid');
    }
}

function toggleContainerActive(container) {
    if (container.querySelector('input[type="text"]:focus') || container.querySelector('textarea:focus')) {
        container.classList.add('active');
    } else {
        container.classList.remove('active');
    }
}


let orders_to_assign = [];

const machineSelector = document.querySelector("#cutting_machines");
const assignButton = document.querySelector("#btn-confirm-assignation");

const searchBar = document.querySelector("#search-order-form");
const inputValue = document.getElementById("search-input");

searchBar.addEventListener('submit', (event) => { 
    event.preventDefault();

    const buildId = inputValue.value;
    const search_url = `/cutting_machine_assignation/api/search-order/?build_id=${buildId}`

    fetch(search_url)

 });

assignButton?.addEventListener("click", () => {

    const selectedMachine = machineSelector?.value;
    console.log(`La machine seleccionada es: ${selectedMachine}`);
    
});
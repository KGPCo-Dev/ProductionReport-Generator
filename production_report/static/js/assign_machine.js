let orders_to_assign = [];
let currentSearchedOrder = null

const machineSelector = document.querySelector("#cutting_machines");
const assignButton = document.querySelector("#btn-confirm-assignation");

const searchBar = document.querySelector("#search-order-form");
const inputValue = document.getElementById("search-input");

searchBar.addEventListener('submit', async (event) => { 
    event.preventDefault();

    const buildId = inputValue.value.trim();
   
    if (!buildId) {
        return;
    }

    try {
        const response = await fetch(`/cutting-machine-assignation/api/search-order/?build_id=${encodeURIComponent(buildId)}`);
        const data = await response.json();

        if (!response.ok) {
            console.log("Response was not ok");
            throw new Error(data.error);
        }

        console.log("Datos de la orden recibidos");

        // ----Data is prepared to be displayed in FrontEnd---- //

        currentSearchedOrder = data;
        document.getElementById("current-build-id").textContent = data.build_id;
        document.getElementById("current-cable-type").textContent = data.cable_length;

        const lengthElem = document.getElementById("current-cable-length");
        if (lengthElem) {
            lengthElem.textContent = data.cable_length + 'ft';
        }

        document.getElementById("search-result-container").style.display = "block";

    } catch(error) {
        console.error("Error", error.message);
        Swal.fire('Atencion', error.message, 'warning');
    }

});

document.getElementById("btn-add-order").addEventListener("click", () => { 
    if(!currentSearchedOrder) return;

    const masterReelInput = document.getElementById("master-reel-input");
    const masterReelValue = masterReelInput.value.trim();

    if (!masterReelValue) {
        Swal.fire("Atención", "Por favor ingresa un Master Reel para agregar esta orden.", "warning");
        return;
    }

    const isDuplicate = orders_to_assign.some(order => order.build_id === currentSearchedOrder.build_id);

    if(isDuplicate) { 
        Swal.fire("Atencion", `La orden ${currentSearchedOrder.build_id} ya esta en tu lista`, "warning");
        return;
    }

    currentSearchedOrder.master_reel = masterReelValue;
    orders_to_assign.push(currentSearchedOrder);
    console.log("Lista actual:",orders_to_assign);

    document.getElementById("search-result-container").style.display = "none";
    inputValue.value = "";
    masterReelInput.value = "";
    currentSearchedOrder = null

    renderOrdersTable();
 });

window.removeOrder = function(index) {
        orders_to_assign.splice(index, 1);
        renderOrdersTable();
    };

function renderOrdersTable() {
    const tbody = document.getElementById("pending-orders-body");
    const section = document.getElementById("pending-orders-section");

    tbody.innerHTML ="";

    if(orders_to_assign.length === 0) {
        section.style.display = "none";
        return;
    }

    section.style.display = "block";

    orders_to_assign.forEach((order, index) => {
        const tr = document.createElement("tr");
        tr.setAttribute('data-index', index);
        tr.style.position = 'relative';
        tr.style.userSelect = 'none'; // Evitar selección de texto al arrastrar
        tr.innerHTML = `
            <td class="text-start">
                <span class="drag-handle text-muted me-2" style="cursor: grab; display: inline-flex; align-items: center;">
                    <i class="bi bi-grip-vertical fs-5"></i>
                </span>
                <span class="fw-semibold">${index + 1}</span>
            </td>
            <td>${order.priority}</td>
            <td>${order.build_id}</td>
            <td>${order.cable_length}</td>
            <td>${order.tethers}</td>
            <td><span class="badge px-2.5 py-1.5 rounded-pill fw-bold" style="font-size: 0.8rem; background-color: #f1f5f9 !important; color: #475569 !important; border: 1px solid #cbd5e1 !important;">${order.master_reel}</span></td>
        `;
        tbody.appendChild(tr);
    });
}

// Inicialización de SortableJS con soporte de drag handle
const sortableTbody = document.getElementById("pending-orders-body");

new Sortable(sortableTbody, {
    animation: 150,
    ghostClass: 'bg-info',
    handle: '.drag-handle', // Solo reordenar al arrastrar desde el grip icon
    onEnd: function(evt) {
        const { oldIndex, newIndex } = evt;
        const movedItem = orders_to_assign.splice(oldIndex, 1)[0];
        orders_to_assign.splice(newIndex, 0, movedItem);
        renderOrdersTable();
        console.log("Arreglo reordenado:", orders_to_assign);
    }
});

// Lógica de Deslizamiento (Swipe to Delete) nativa
let swipeStart = null;

sortableTbody.addEventListener('mousedown', startSwipe);
sortableTbody.addEventListener('touchstart', startSwipe, { passive: true });

function startSwipe(e) {
    // Si el clic es en la manija de drag, dejamos que actúe SortableJS
    if (e.target.closest('.drag-handle')) {
        return;
    }

    const tr = e.target.closest('tr');
    if (!tr) return;

    const clientX = e.type.startsWith('touch') ? e.touches[0].clientX : e.clientX;
    const clientY = e.type.startsWith('touch') ? e.touches[0].clientY : e.clientY;

    swipeStart = {
        startX: clientX,
        startY: clientY,
        tr: tr,
        index: parseInt(tr.getAttribute('data-index')),
        width: tr.offsetWidth,
        isScrolling: false,
        isSwiping: false
    };

    tr.classList.remove('swipe-animate');

    document.addEventListener('mousemove', moveSwipe);
    document.addEventListener('touchmove', moveSwipe, { passive: false });
    document.addEventListener('mouseup', endSwipe);
    document.addEventListener('touchend', endSwipe);
}

function moveSwipe(e) {
    if (!swipeStart) return;

    const clientX = e.type.startsWith('touch') ? e.touches[0].clientX : e.clientX;
    const clientY = e.type.startsWith('touch') ? e.touches[0].clientY : e.clientY;

    const diffX = clientX - swipeStart.startX;
    const diffY = clientY - swipeStart.startY;

    // Detectar si el usuario está haciendo scroll vertical o swipe horizontal
    if (!swipeStart.isSwiping && !swipeStart.isScrolling) {
        if (Math.abs(diffX) > Math.abs(diffY)) {
            swipeStart.isSwiping = true;
        } else {
            swipeStart.isScrolling = true;
        }
    }

    if (swipeStart.isScrolling) {
        return;
    }

    if (swipeStart.isSwiping && diffX > 0) {
        if (e.cancelable) e.preventDefault();

        // Desplazar visualmente la fila a la derecha
        swipeStart.tr.style.transform = `translateX(${diffX}px)`;

        const threshold = swipeStart.width * 0.35;
        if(diffX > threshold) {
            swipeStart.tr.classList.add('swipe-danger');
        } else {
            swipeStart.tr.classList.remove('swipe-danger');
        }
    }
}

function endSwipe(e) {
    if (!swipeStart) return;

    const clientX = e.type.startsWith('touch') ? e.changedTouches[0].clientX : e.clientX;
    const diffX = clientX - swipeStart.startX;
    const threshold = swipeStart.width * 0.35;

    const tr = swipeStart.tr;
    const index = swipeStart.index;

    document.removeEventListener('mousemove', moveSwipe);
    document.removeEventListener('touchmove', moveSwipe);
    document.removeEventListener('mouseup', endSwipe);
    document.removeEventListener('touchend', endSwipe);

    const isDeleted = swipeStart.isSwiping && diffX > threshold;
    swipeStart = null;

    tr.classList.add('swipe-animate');

    if (isDeleted) {
        tr.style.transform = `translateX(${tr.offsetWidth}px)`
        tr.style.opacity = '0';
        setTimeout (() => {
            removeOrder(index);
        }, 300);
    } else {
        tr.style.transform = `translateX(0px)`;
        tr.classList.remove('swipe-danger');
    }
}

assignButton?.addEventListener("click", () => {

    const selectedMachine = machineSelector?.value;

    if (orders_to_assign.length === 0) {
        Swal.fire("Atencion", "No has agregado ninguna orden a la lista", "warning");
        return;
    }

    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

    const ordersPayload = orders_to_assign.map((order, index) => ({
        build_id: order.build_id,
        master_reel: order.master_reel,
        stack_id: index + 1
    }));

    const payload = {
        machine: selectedMachine,
        orders: ordersPayload
    };

    console.log("Payload a enviar:", payload);

    Swal.fire({ title: 'Guardando...', allowOutsideClick: false, didOpen: () => { Swal.showLoading(); } });

    fetch('/cutting-machine-assignation/api/save-assignation/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrfToken },
        body: JSON.stringify(payload)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            Swal.fire('¡Éxito!', data.message, 'success');
            
            // Actualizar de forma inmediata el contador en la tarjeta de la máquina seleccionada
            const activeCard = document.querySelector(`.machine-card[data-machine-code="${selectedMachine}"]`);
            if (activeCard) {
                const descElem = activeCard.querySelector('.description-text');
                if (descElem) {
                    const match = descElem.textContent.match(/\d+/);
                    if (match) {
                        const currentCount = parseInt(match[0]);
                        const newCount = currentCount + orders_to_assign.length;
                        descElem.textContent = `Ordenes Asignadas: ${newCount}`;
                    }
                }
            }

            // ¡Limpiamos nuestro estado y repintamos la vista!
            orders_to_assign = [];
            renderOrdersTable();
            
        } else {
            Swal.fire('Error', data.error || 'Ocurrió un problema.', 'error');
        }
    })
    .catch(error => {
        console.error('Error en la peticion POST al asignar ordenes:', error);
        Swal.fire('Error de Red', 'No se pudo conectar con el servidor', 'error');
    });
});

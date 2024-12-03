let html5QrcodeScanner = null;
let currentCamera = 'environment';

function toggleCamera() {
    currentCamera = currentCamera === 'environment' ? 'user' : 'environment';
    if (html5QrcodeScanner) {
        stopScanner().then(() => {
            startScanner();
        });
    }
}

function toggleScanner() {
    if (html5QrcodeScanner === null) {
        html5QrcodeScanner = new Html5Qrcode("reader");
        startScanner();
        document.getElementById('scannerToggle').textContent = 'Stop Scanner';
    } else {
        stopScanner();
        document.getElementById('scannerToggle').textContent = 'Start Scanner';
    }
}

function startScanner() {
    const config = {
        fps: 10,
        qrbox: { width: 250, height: 250 },
        aspectRatio: 1.0
    };

    html5QrcodeScanner.start(
        { facingMode: currentCamera },
        config,
        onScanSuccess,
        onScanError
    );
}

async function stopScanner() {
    if (html5QrcodeScanner) {
        await html5QrcodeScanner.stop();
        html5QrcodeScanner = null;
    }
}

function onScanSuccess(decodedText, decodedResult) {
    // Play success sound
    const audio = new Audio('/static/sounds/beep.mp3');
    audio.play();

    // Show quick actions
    showQuickActions(decodedText);
}

function onScanError(error) {
    // Handle scan error silently
    console.warn(`QR Code scan error: ${error}`);
}

function showQuickActions(sku) {
    const quickActions = document.getElementById('quick-actions');
    quickActions.innerHTML = `
        <p>SKU: ${sku}</p>
        <button onclick="updateStock('${sku}', 'add')" class="add">
            Add One (+1)
        </button>
        <button onclick="updateStock('${sku}', 'remove')" class="remove">
            Remove One (-1)
        </button>
    `;
    quickActions.classList.add('visible');
}

async function generateQR(sku) {
    const response = await fetch(`/generate_qr/${sku}`);
    const data = await response.json();
    const qrDiv = document.getElementById(`qr-${sku}`);
    qrDiv.innerHTML = `<img src="data:image/png;base64,${data.qr_code}" alt="QR Code">`;
}

async function updateStock(sku, action) {
    const response = await fetch('/update_stock', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ sku, action }),
    });
    
    const data = await response.json();
    if (data.success) {
        document.getElementById(`quantity-${sku}`).textContent = data.new_quantity;
        
        // Update quick actions if they're visible
        let quickActions = document.querySelector('.quick-actions');
        if (quickActions) {
            quickActions.remove();
        }
    }
}

async function syncEbay() {
    const response = await fetch('/sync_ebay');
    const data = await response.json();
    if (data.success) {
        alert('Successfully synced with eBay!');
        location.reload();
    } else {
        alert('Error syncing with eBay: ' + data.error);
    }
} 
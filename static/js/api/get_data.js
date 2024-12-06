document.addEventListener('DOMContentLoaded', function() {
    const logTableBody = document.getElementById('log-table-body');

    // Fonction pour ajouter une ligne dans le tableau
    function addLogRow(log) {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${log.user}</td>
            <td>${log.endpoint}</td>
            <td>${log.method}</td>
            <td>${log.timestamp}</td>
        `;
        logTableBody.appendChild(row);
    }

    // Fonction pour récupérer les logs via AJAX
    function fetchLogs() {
        const token = localStorage.getItem('access_token');
        if (!token) {
            console.error("Token JWT non trouvé dans localStorage");
            return;
        }

        fetch('/api/get-logs', {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.logs) {
                logTableBody.innerHTML = '';  // Réinitialiser les logs existants
                data.logs.forEach(log => addLogRow(log));  // Ajouter chaque log à la table
            } else {
                console.error("Les logs sont dans un format inattendu:", data);
            }
        })
        .catch(error => {
            console.error("Erreur lors de la récupération des logs:", error);
        });
    }

    // Appeler la fonction pour charger les logs lorsque la page est chargée
    fetchLogs();
});

document.addEventListener('DOMContentLoaded', function() {
    const refreshButton = document.getElementById('refresh-button');

    // Lorsqu'on clique sur le bouton, on recharge la page
    refreshButton.addEventListener('click', function() {
        location.reload();
    });
});

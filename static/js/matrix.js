document.addEventListener("DOMContentLoaded", () => {
    // 0. Web Push Notification Permission & Status Badge
    const pushStatusBadge = document.getElementById("pushStatusBadge");
    const enablePushBtn = document.getElementById("enablePushBtn");

    function updatePushStatus() {
        if (!("Notification" in window)) {
            if (pushStatusBadge) {
                pushStatusBadge.className = "badge bg-danger";
                pushStatusBadge.innerText = "Unsupported";
            }
            return;
        }

        if (Notification.permission === "granted") {
            if (pushStatusBadge) {
                pushStatusBadge.className = "badge bg-success";
                pushStatusBadge.innerHTML = `<i class="bi bi-check-circle-fill me-1"></i>Active`;
            }
            if (enablePushBtn) enablePushBtn.style.display = "none";
        } else if (Notification.permission === "denied") {
            if (pushStatusBadge) {
                pushStatusBadge.className = "badge bg-danger";
                pushStatusBadge.innerHTML = `<i class="bi bi-x-circle-fill me-1"></i>Blocked`;
            }
            if (enablePushBtn) {
                enablePushBtn.style.display = "inline-block";
                enablePushBtn.innerText = "Blocked in Browser";
                enablePushBtn.title = "Click the lock icon in your browser URL bar to allow notifications";
            }
        } else {
            if (pushStatusBadge) {
                pushStatusBadge.className = "badge bg-warning text-dark";
                pushStatusBadge.innerText = "Permission Required";
            }
            if (enablePushBtn) {
                enablePushBtn.style.display = "inline-block";
                enablePushBtn.innerHTML = `<i class="bi bi-bell-fill me-1"></i>Enable Push`;
            }
        }
    }

    updatePushStatus();

    if (enablePushBtn) {
        enablePushBtn.addEventListener("click", async () => {
            if (!("Notification" in window)) {
                alert("Your browser does not support desktop push notifications.");
                return;
            }
            // Also prompt OneSignal subscription if SDK is loaded
            if (window.OneSignalDeferred) {
                OneSignalDeferred.push(async function(OneSignal) {
                    try {
                        await OneSignal.Slidedown.promptPush();
                    } catch (e) {
                        console.log("OneSignal prompt:", e);
                    }
                });
            }

            const permission = await Notification.requestPermission();
            updatePushStatus();
            if (permission === "granted") {
                new Notification("Starclinch Notifications Active! 🔔", {
                    body: "Web Push notifications are now enabled. Test any trigger in the table!",
                    icon: "https://cdn-icons-png.flaticon.com/512/1827/1827392.png"
                });
            } else if (permission === "denied") {
                alert("Notifications were blocked. Please click the lock icon in your address bar and change Notifications to 'Allow'.");
            }
        });
    }

    // 1. Channel On / Off Toggles
    document.querySelectorAll(".toggle-btn").forEach(switchEl => {
        switchEl.addEventListener("change", async (e) => {
            const templateId = e.target.dataset.id;
            const cell = document.getElementById(`cell-${templateId}`);
            try {
                const res = await fetch(`/api/template/${templateId}/toggle/`, {
                    method: "POST",
                    headers: {"Content-Type": "application/json"}
                });
                const data = await res.json();
                if (data.success) {
                    if (data.is_enabled) {
                        cell.classList.remove("cell-disabled");
                    } else {
                        cell.classList.add("cell-disabled");
                    }
                }
            } catch (err) {
                alert("Error toggling channel status");
            }
        });
    });

    // 2. Open Edit Modal
    const editModal = new bootstrap.Modal(document.getElementById("editModal"));
    document.querySelectorAll(".edit-btn").forEach(btn => {
        btn.addEventListener("click", () => {
            document.getElementById("modalTemplateId").value = btn.dataset.id;
            document.getElementById("modalTemplateTitle").value = btn.dataset.title;
            document.getElementById("modalTemplateBody").value = btn.dataset.body;
            editModal.show();
        });
    });

    // 3. Save Modal Changes
    document.getElementById("saveModalBtn").addEventListener("click", async () => {
        const id = document.getElementById("modalTemplateId").value;
        const title = document.getElementById("modalTemplateTitle").value;
        const body = document.getElementById("modalTemplateBody").value;

        try {
            const res = await fetch(`/api/template/${id}/save/`, {
                method: "POST",
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify({title, body})
            });
            const data = await res.json();
            if (data.success) {
                location.reload();
            }
        } catch (err) {
            alert("Error saving template");
        }
    });

    // 4. Test Send Button (with Native Browser Push Notification!)
    document.querySelectorAll(".test-btn").forEach(btn => {
        btn.addEventListener("click", async () => {
            const templateId = btn.dataset.id;
            const originalHTML = btn.innerHTML;
            btn.innerHTML = `<span class="spinner-border spinner-border-sm"></span> Sending...`;
            btn.disabled = true;

            try {
                const res = await fetch(`/api/template/${templateId}/test-send/`, {
                    method: "POST",
                    headers: {"Content-Type": "application/json"}
                });
                const data = await res.json();

                // If testing Web Push, show native browser popup right on screen!
                if (data.channel === "web_push") {
                    if (window.Notification && Notification.permission === "granted") {
                        new Notification(data.title || "Starclinch Notification", {
                            body: data.body,
                            icon: "https://cdn-icons-png.flaticon.com/512/1827/1827392.png"
                        });
                    } else if (window.Notification && Notification.permission === "denied") {
                        alert("⚠️ Notification sent to backend, but your browser is blocking desktop popups!\n\nPlease click the lock icon in your address bar and change Notifications to 'Allow'.");
                    } else if (window.Notification) {
                        Notification.requestPermission().then(permission => {
                            updatePushStatus();
                            if (permission === "granted") {
                                new Notification(data.title || "Starclinch Notification", { body: data.body });
                            }
                        });
                    }
                }

                const resStatus = data.result?.status;
                const resDetail = data.result?.result?.response || data.result?.result?.error || "";

                if (resStatus === "SUCCESS") {
                    btn.classList.remove("btn-outline-success", "btn-outline-warning");
                    btn.classList.add("btn-success");
                    btn.innerHTML = `<i class="bi bi-check-circle"></i> Sent!`;
                } else {
                    btn.classList.remove("btn-outline-success", "btn-outline-warning");
                    btn.classList.add("btn-danger");
                    btn.innerHTML = `<i class="bi bi-x-circle"></i> Failed`;
                    alert(`Notification Failed:\n\n${resDetail || "Please verify credentials in environment variables."}`);
                }

                // Refresh table to show the new log entry
                setTimeout(() => location.reload(), 1500);
            } catch (err) {
                alert("Failed to send test notification: " + err.message);
                btn.innerHTML = originalHTML;
                btn.disabled = false;
            }
        });
    });
});

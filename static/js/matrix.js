document.addEventListener("DOMContentLoaded", () => {
    // Request Desktop Notification Permission on load
    if ("Notification" in window && Notification.permission === "default") {
        Notification.requestPermission();
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
                    if (Notification.permission === "granted") {
                        new Notification(data.title || "Starclinch Notification", {
                            body: data.body,
                            icon: "https://cdn-icons-png.flaticon.com/512/1827/1827392.png"
                        });
                    } else if (Notification.permission !== "denied") {
                        Notification.requestPermission().then(permission => {
                            if (permission === "granted") {
                                new Notification(data.title, { body: data.body });
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

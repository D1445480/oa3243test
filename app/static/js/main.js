/**
 * 校園活動資訊整合平台 - 全域前端邏輯 (AJAX 收藏處理)
 */

document.addEventListener("DOMContentLoaded", () => {
    // 綁定所有收藏按鈕的點擊事件
    const favButtons = document.querySelectorAll(".btn-fav-toggle");
    
    favButtons.forEach(btn => {
        btn.addEventListener("click", async (e) => {
            e.preventDefault();
            e.stopPropagation(); // 阻止氣泡事件，防止觸發卡片點擊重導向
            
            const eventId = btn.getAttribute("data-event-id");
            if (!eventId) return;
            
            try {
                // 發送 POST 請求切換收藏狀態
                const response = await fetch(`/favorite/toggle/${eventId}`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        // 如果有 CSRF Token，可以在此處加入
                    }
                });
                
                // 如果回傳 401 Unauthorized，代表使用者未登入，引導至登入頁面
                if (response.status === 401) {
                    showToast("請先登入系統才能使用收藏功能！", "warning");
                    setTimeout(() => {
                        window.location.href = "/auth/login";
                    }, 1200);
                    return;
                }
                
                // 如果回傳 403 Forbidden，代表權限不足（例如主辦單位無法收藏）
                if (response.status === 403) {
                    const data = await response.json();
                    showToast(data.message || "只有一般學生帳號可使用收藏功能。", "danger");
                    return;
                }
                
                if (!response.ok) {
                    throw new Error("網路連線或伺服器回應異常。");
                }
                
                const result = await response.json();
                
                if (result.status === "success") {
                    const icon = btn.querySelector("i");
                    
                    if (result.action === "favorited") {
                        btn.classList.add("favorited");
                        if (icon) {
                            icon.className = "bi bi-heart-fill";
                        }
                        showToast(result.message, "success");
                    } else if (result.action === "unfavorited") {
                        btn.classList.remove("favorited");
                        if (icon) {
                            icon.className = "bi bi-heart";
                        }
                        showToast(result.message, "info");
                        
                        // 若目前在「我的收藏」頁面，自動將該活動卡片從畫面移除
                        if (window.location.pathname === "/favorite/my-favorites") {
                            const cardCol = btn.closest(".event-card-col");
                            if (cardCol) {
                                cardCol.style.transition = "all 0.4s ease";
                                cardCol.style.opacity = "0";
                                cardCol.style.transform = "scale(0.8)";
                                setTimeout(() => {
                                    cardCol.remove();
                                    // 檢查是否已無收藏卡片，若無則顯示空狀態
                                    const remainingCards = document.querySelectorAll(".event-card-col");
                                    if (remainingCards.length === 0) {
                                        location.reload(); // 重新整理頁面以顯示預設的空收藏頁面
                                    }
                                }, 400);
                            }
                        }
                    }
                } else {
                    showToast(result.message || "操作失敗，請稍後再試。", "danger");
                }
            } catch (error) {
                console.error("收藏請求出錯:", error);
                showToast("連線伺服器時出錯，請檢查網路連線。", "danger");
            }
        });
    });
});

/**
 * 動態產生並顯示一個簡約的 Toast 提示框
 * @param {string} message 提示訊息內容
 * @param {string} type 類型 ('success', 'warning', 'danger', 'info')
 */
function showToast(message, type = "success") {
    // 檢查全域的 Toast 容器是否存在，不存在則建立
    let container = document.querySelector(".flash-container");
    if (!container) {
        container = document.createElement("div");
        container.className = "flash-container";
        document.body.appendChild(container);
    }
    
    // 建立 Toast 元素
    const alertDiv = document.createElement("div");
    alertDiv.className = `alert alert-custom alert-dismissible fade show p-3 mb-2`;
    alertDiv.role = "alert";
    
    // 依類型設定圖示
    let iconClass = "bi-check-circle-fill text-success";
    if (type === "warning") iconClass = "bi-exclamation-triangle-fill text-warning";
    if (type === "danger") iconClass = "bi-x-circle-fill text-danger";
    if (type === "info") iconClass = "bi-info-circle-fill text-info";
    
    alertDiv.innerHTML = `
        <div class="d-flex align-items-center gap-2">
            <i class="bi ${iconClass}"></i>
            <span>${message}</span>
        </div>
        <button type="button" class="btn-close btn-close-white" data-bs-dismiss="alert" aria-label="Close" style="font-size: 0.75rem; margin-top: 1px;"></button>
    `;
    
    container.appendChild(alertDiv);
    
    // 3 秒後自動關閉
    setTimeout(() => {
        // 使用 Bootstrap 的 Alert 類別關閉
        const alertInstance = bootstrap.Alert.getOrCreateInstance(alertDiv);
        if (alertInstance) {
            alertInstance.close();
        } else {
            alertDiv.remove();
        }
    }, 3000);
}

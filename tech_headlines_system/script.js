// 双语科技头条系统 - 交互功能

document.addEventListener('DOMContentLoaded', function() {
    // 初始化所有功能
    initLanguageSwitcher();
    initCategoryNavigation();
    initCharts();
    initFormValidation();
    updateDynamicContent();
    
    // 设置自动刷新（可选）
    setInterval(updateLastUpdateTime, 60000); // 每分钟更新一次时间
});

// 语言切换功能
function initLanguageSwitcher() {
    const langButtons = document.querySelectorAll('.lang-btn');
    const currentLang = localStorage.getItem('preferredLanguage') || 'zh';
    
    // 设置初始语言
    setLanguage(currentLang);
    
    // 添加点击事件
    langButtons.forEach(button => {
        button.addEventListener('click', function() {
            const lang = this.dataset.lang;
            setLanguage(lang);
            localStorage.setItem('preferredLanguage', lang);
            
            // 更新按钮状态
            langButtons.forEach(btn => btn.classList.remove('active'));
            this.classList.add('active');
            
            // 重新初始化图表（因为标签需要更新）
            initCharts();
        });
    });
}

function setLanguage(lang) {
    // 更新所有双语内容
    document.querySelectorAll('[data-zh], [data-en]').forEach(element => {
        const text = element.dataset[lang];
        if (text) {
            if (element.tagName === 'INPUT' || element.tagName === 'TEXTAREA') {
                element.placeholder = text;
            } else {
                element.textContent = text;
            }
        }
    });
    
    // 更新页面语言属性
    document.documentElement.lang = lang;
    
    // 保存语言偏好
    localStorage.setItem('preferredLanguage', lang);
    
    // 触发自定义事件
    document.dispatchEvent(new CustomEvent('languageChanged', { detail: { lang } }));
}

// 分类导航功能
function initCategoryNavigation() {
    const navButtons = document.querySelectorAll('.nav-btn');
    const contentSections = document.querySelectorAll('.content-section');
    
    // 设置初始激活的分类
    const activeCategory = localStorage.getItem('activeCategory') || 'ai';
    showCategory(activeCategory);
    
    navButtons.forEach(button => {
        button.addEventListener('click', function() {
            const category = this.dataset.category;
            showCategory(category);
            localStorage.setItem('activeCategory', category);
            
            // 更新按钮状态
            navButtons.forEach(btn => btn.classList.remove('active'));
            this.classList.add('active');
            
            // 滚动到顶部
            window.scrollTo({ top: 0, behavior: 'smooth' });
        });
    });
}

function showCategory(category) {
    // 隐藏所有内容区域
    document.querySelectorAll('.content-section').forEach(section => {
        section.classList.remove('active');
    });
    
    // 显示选中的内容区域
    const targetSection = document.getElementById(`${category}-content`);
    if (targetSection) {
        targetSection.classList.add('active');
    }
    
    // 更新URL哈希（可选）
    window.location.hash = `#${category}`;
}

// 图表初始化
function initCharts() {
    // AI趋势图表
    const aiTrendCtx = document.getElementById('ai-trend-chart');
    if (aiTrendCtx) {
        const currentLang = localStorage.getItem('preferredLanguage') || 'zh';
        const labels = currentLang === 'zh' 
            ? ['2026', '2027', '2028', '2029', '2030']
            : ['2026', '2027', '2028', '2029', '2030'];
        
        const labelText = currentLang === 'zh' ? '市场规模 (十亿美元)' : 'Market Size ($B)';
        
        new Chart(aiTrendCtx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: labelText,
                    data: [25, 45, 78, 120, 180],
                    borderColor: '#2563eb',
                    backgroundColor: 'rgba(37, 99, 235, 0.1)',
                    borderWidth: 3,
                    fill: true,
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        labels: {
                            font: {
                                size: 14
                            }
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const value = context.raw;
                                const suffix = currentLang === 'zh' ? '十亿美元' : 'B';
                                return `${labelText}: ${value}${suffix}`;
                            }
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            callback: function(value) {
                                const suffix = currentLang === 'zh' ? '十亿' : 'B';
                                return value + suffix;
                            }
                        }
                    }
                }
            }
        });
    }
    
    // 可以添加更多图表...
}

// 表单验证
function initFormValidation() {
    const subscribeForm = document.querySelector('.subscribe-form');
    if (subscribeForm) {
        const emailInput = subscribeForm.querySelector('input[type="email"]');
        const submitButton = subscribeForm.querySelector('button');
        
        submitButton.addEventListener('click', function(e) {
            e.preventDefault();
            
            if (!emailInput.value) {
                showNotification('请输入邮箱地址', 'error');
                return;
            }
            
            if (!isValidEmail(emailInput.value)) {
                showNotification('请输入有效的邮箱地址', 'error');
                return;
            }
            
            // 模拟订阅成功
            showNotification('订阅成功！感谢关注科技头条', 'success');
            emailInput.value = '';
            
            // 这里可以添加实际的订阅逻辑
            // subscribeToNewsletter(emailInput.value);
        });
    }
}

function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

// 通知系统
function showNotification(message, type = 'info') {
    // 移除现有的通知
    const existingNotification = document.querySelector('.notification');
    if (existingNotification) {
        existingNotification.remove();
    }
    
    // 创建新通知
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <div class="notification-content">
            <i class="fas ${getNotificationIcon(type)}"></i>
            <span>${message}</span>
        </div>
        <button class="notification-close"><i class="fas fa-times"></i></button>
    `;
    
    // 添加到页面
    document.body.appendChild(notification);
    
    // 添加样式
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: ${getNotificationColor(type)};
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 0.5rem;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 1rem;
        z-index: 1000;
        animation: slideIn 0.3s ease;
        max-width: 400px;
    `;
    
    // 添加动画
    const style = document.createElement('style');
    style.textContent = `
        @keyframes slideIn {
            from { transform: translateX(100%); opacity: 0; }
            to { transform: translateX(0); opacity: 1; }
        }
        .notification-content {
            display: flex;
            align-items: center;
            gap: 0.75rem;
        }
        .notification-close {
            background: none;
            border: none;
            color: white;
            cursor: pointer;
            padding: 0.25rem;
            opacity: 0.8;
            transition: opacity 0.2s;
        }
        .notification-close:hover {
            opacity: 1;
        }
    `;
    document.head.appendChild(style);
    
    // 关闭按钮事件
    notification.querySelector('.notification-close').addEventListener('click', () => {
        notification.remove();
    });
    
    // 自动关闭
    setTimeout(() => {
        if (notification.parentNode) {
            notification.style.animation = 'slideOut 0.3s ease';
            setTimeout(() => notification.remove(), 300);
        }
    }, 5000);
}

function getNotificationIcon(type) {
    switch(type) {
        case 'success': return 'fa-check-circle';
        case 'error': return 'fa-exclamation-circle';
        case 'warning': return 'fa-exclamation-triangle';
        default: return 'fa-info-circle';
    }
}

function getNotificationColor(type) {
    switch(type) {
        case 'success': return '#10b981';
        case 'error': return '#ef4444';
        case 'warning': return '#f59e0b';
        default: return '#3b82f6';
    }
}

// 动态内容更新
function updateDynamicContent() {
    // 更新最后更新时间
    updateLastUpdateTime();
    
    // 检查新内容（这里可以添加实际的API调用）
    // checkForNewContent();
}

function updateLastUpdateTime() {
    const now = new Date();
    const timeElements = document.querySelectorAll('.last-update span');
    
    const options = { 
        year: 'numeric', 
        month: 'long', 
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    };
    
    timeElements.forEach(element => {
        const currentLang = localStorage.getItem('preferredLanguage') || 'zh';
        if (currentLang === 'zh') {
            const zhTime = now.toLocaleString('zh-CN', options);
            element.dataset.zh = `更新于: ${zhTime}`;
        } else {
            const enTime = now.toLocaleString('en-US', options);
            element.dataset.en = `Updated: ${enTime}`;
        }
        
        // 立即更新显示
        element.textContent = currentLang === 'zh' ? element.dataset.zh : element.dataset.en;
    });
}

// 分享功能
function initShareButtons() {
    // 可以添加社交媒体分享按钮
    // 例如：分享到Twitter、Telegram等
}

// 离线支持
if ('serviceWorker' in navigator) {
    window.addEventListener('load', function() {
        navigator.serviceWorker.register('/sw.js').then(
            function(registration) {
                console.log('ServiceWorker 注册成功: ', registration.scope);
            },
            function(err) {
                console.log('ServiceWorker 注册失败: ', err);
            }
        );
    });
}

// 性能监控
const perfObserver = new PerformanceObserver((list) => {
    for (const entry of list.getEntries()) {
        console.log(`${entry.name}: ${entry.duration}ms`);
    }
});

perfObserver.observe({ entryTypes: ['largest-contentful-paint', 'first-input'] });

// 错误监控
window.addEventListener('error', function(event) {
    console.error('页面错误:', event.error);
    // 这里可以添加错误上报逻辑
});

// 键盘快捷键
document.addEventListener('keydown', function(event) {
    // 切换语言: Ctrl/Cmd + L
    if ((event.ctrlKey || event.metaKey) && event.key === 'l') {
        event.preventDefault();
        const currentLang = localStorage.getItem('preferredLanguage') || 'zh';
        const newLang = currentLang === 'zh' ? 'en' : 'zh';
        setLanguage(newLang);
        
        // 更新按钮状态
        document.querySelectorAll('.lang-btn').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.lang === newLang);
        });
    }
    
    // 切换分类: 数字键1-5
    if (event.key >= '1' && event.key <= '5') {
        const categories = ['ai', 'quantum', 'materials', 'web3', 'security'];
        const index = parseInt(event.key) - 1;
        if (categories[index]) {
            showCategory(categories[index]);
            
            // 更新按钮状态
            document.querySelectorAll('.nav-btn').forEach(btn => {
                btn.classList.toggle('active', btn.dataset.category === categories[index]);
            });
        }
    }
});

// 导出功能（如果需要）
window.techHeadlines = {
    setLanguage,
    showCategory,
    showNotification,
    updateLastUpdateTime
};
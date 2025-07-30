// カウントアップアニメーション
function animateValue(element, start, end, duration) {
    let startTimestamp = null;
    const step = (timestamp) => {
        if (!startTimestamp) startTimestamp = timestamp;
        const progress = Math.min((timestamp - startTimestamp) / duration, 1);
        element.innerText = Math.floor(progress * (end - start) + start);
        if (progress < 1) {
            window.requestAnimationFrame(step);
        }
    };
    window.requestAnimationFrame(step);
}

// スクロール時のナビゲーション表示
let lastScrollTop = 0;
const navbar = document.getElementById('navbar');

window.addEventListener('scroll', () => {
    const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
    
    if (scrollTop > 100) {
        navbar.classList.add('visible');
    } else {
        navbar.classList.remove('visible');
    }
    
    lastScrollTop = scrollTop;
});

// スムーススクロール
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            const offset = 80; // ナビゲーションの高さ分オフセット
            const targetPosition = target.offsetTop - offset;
            window.scrollTo({
                top: targetPosition,
                behavior: 'smooth'
            });
        }
    });
});

// Intersection Observer でアニメーション発火
const observerOptions = {
    threshold: 0.3,
    rootMargin: '0px 0px -100px 0px'
};

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            // 統計数値のカウントアップ
            if (entry.target.classList.contains('hero-stats')) {
                entry.target.querySelectorAll('.stat-number').forEach(stat => {
                    const target = parseInt(stat.getAttribute('data-target'));
                    animateValue(stat, 0, target, 2000);
                });
                observer.unobserve(entry.target);
            }
            
            // フェードインアニメーション
            if (entry.target.hasAttribute('data-aos')) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        }
    });
}, observerOptions);

// 監視対象の要素を登録
document.querySelectorAll('.hero-stats').forEach(el => observer.observe(el));
document.querySelectorAll('[data-aos]').forEach(el => {
    el.style.opacity = '0';
    el.style.transform = 'translateY(20px)';
    el.style.transition = 'all 0.6s ease-out';
    observer.observe(el);
});

// 投資シミュレーター
const propertyCountSlider = document.getElementById('property-count');
const occupancyRateSlider = document.getElementById('occupancy-rate');
const propertyCountDisplay = document.getElementById('property-count-display');
const occupancyRateDisplay = document.getElementById('occupancy-rate-display');
const annualRevenueDisplay = document.getElementById('annual-revenue');
const annualProfitDisplay = document.getElementById('annual-profit');
const paybackPeriodDisplay = document.getElementById('payback-period');

function updateCalculator() {
    const propertyCount = parseInt(propertyCountSlider.value);
    const occupancyRate = parseInt(occupancyRateSlider.value) / 100;
    
    // 表示更新
    propertyCountDisplay.textContent = propertyCount;
    occupancyRateDisplay.textContent = Math.round(occupancyRate * 100);
    
    // 計算（実際のモデルベース）
    const baseRevenue = 300; // 基本年間売上（万円）
    const adjustedRevenue = baseRevenue * (occupancyRate / 0.33); // 稼働率33%基準で調整
    const totalRevenue = adjustedRevenue * propertyCount;
    
    // 自社所有と賃貸の比率（1:1）
    const ownedProperties = Math.floor(propertyCount / 2);
    const rentedProperties = propertyCount - ownedProperties;
    
    // 利益計算（実際のモデル値）
    const ownedProfit = ownedProperties * 236 * (occupancyRate / 0.33); // NOI 236万円
    const rentedProfit = rentedProperties * 150.6 * (occupancyRate / 0.33); // 営業利益 150.6万円
    const totalProfit = ownedProfit + rentedProfit;
    
    // 投資額計算（実際のモデル値）
    const ownedInvestment = ownedProperties * 1890; // 1890万円/物件
    const rentedInvestment = rentedProperties * 550; // 550万円/物件
    const totalInvestment = ownedInvestment + rentedInvestment;
    
    // 投資回収期間
    const paybackPeriod = totalInvestment / totalProfit;
    
    // 表示更新
    annualRevenueDisplay.textContent = `${totalRevenue.toLocaleString()}万円`;
    annualProfitDisplay.textContent = `${Math.round(totalProfit).toLocaleString()}万円`;
    paybackPeriodDisplay.textContent = `${paybackPeriod.toFixed(1)}年`;
}

propertyCountSlider.addEventListener('input', updateCalculator);
occupancyRateSlider.addEventListener('input', updateCalculator);

// 初期計算実行
updateCalculator();

// 成長チャート
const ctx = document.getElementById('growth-chart');
if (ctx) {
    const growthChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: ['1年目', '2年目', '3年目', '4年目', '5年目'],
            datasets: [{
                label: '年間売上（百万円）',
                data: [30, 30, 60, 60, 90],
                borderColor: '#1e3c72',
                backgroundColor: 'rgba(30, 60, 114, 0.1)',
                tension: 0.4,
                fill: true
            }, {
                label: '年間営業利益（百万円）',
                data: [19.3, 19.3, 38.7, 38.7, 58.0],
                borderColor: '#ff6b6b',
                backgroundColor: 'rgba(255, 107, 107, 0.1)',
                tension: 0.4,
                fill: true
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: '5年間の成長予測',
                    font: {
                        size: 18,
                        family: 'Noto Sans JP'
                    }
                },
                legend: {
                    position: 'bottom'
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: '金額（百万円）'
                    }
                }
            }
        }
    });
}

// フォーム送信処理
const contactForm = document.getElementById('contact-form');
if (contactForm) {
    contactForm.addEventListener('submit', (e) => {
        e.preventDefault();
        
        // ここで実際の送信処理を行う
        alert('お問い合わせありがとうございます。追ってご連絡させていただきます。');
        contactForm.reset();
    });
}

// パララックス効果
window.addEventListener('scroll', () => {
    const scrolled = window.pageYOffset;
    const hero = document.querySelector('.hero');
    if (hero) {
        hero.style.transform = `translateY(${scrolled * 0.5}px)`;
    }
});
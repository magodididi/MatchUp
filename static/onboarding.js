class OnboardingTour {
    constructor() {
        this.steps = [
            {
                element: '.profile-circle',
                title: '👤 Твой профиль',
                description: 'Здесь ты можешь отредактировать свои фото, интересы и информацию о себе',
                position: 'bottom'
            },
            {
                element: '.matches-btn',
                title: '💕 Твои матчи',
                description: 'Сюда попадают люди, которым ты понравился и которые понравились тебе',
                position: 'bottom'
            },
            {
                element: '.swipe-container .card',
                title: '❤️ Свайп',
                description: 'Листай анкеты: нажми ❤️ если нравится, или ❌ чтобы пропустить',
                position: 'top'
            },
            {
                element: '.actions',
                title: '👍👎 Действия',
                description: 'Можно нажимать кнопки или использовать стрелки ← и → на клавиатуре',
                position: 'top'
            },
            {
                element: '.common',
                title: '✨ Общие интересы',
                description: 'Мы показываем людей с похожими увлечениями. Больше общих интересов - выше шанс на матч!',
                position: 'bottom'
            }
        ];
        
        this.currentStep = 0;
        this.overlay = null;
        this.tooltip = null;
        this.isActive = false;
    }
    
    start() {
        // Проверяем, новый ли пользователь (нет матчей и не заполнен профиль)
        const hasMatches = document.querySelector('.match-grid')?.children.length > 0;
        const profileProgress = document.querySelector('.progress-bar-fill')?.style.width;
        const progressPercent = profileProgress ? parseInt(profileProgress) : 0;
        
        // Показываем тур если пользователь новый (профиль заполнен менее чем на 30%)
        if (progressPercent < 30 && !localStorage.getItem('onboardingCompleted')) {
            setTimeout(() => this.init(), 1000);
        }
    }
    
    init() {
        this.isActive = true;
        this.createOverlay();
        this.createTooltip();
        this.showStep(0);
        
        // Блокируем скролл
        document.body.style.overflow = 'hidden';
        
        // Добавляем обработчик клавиш
        document.addEventListener('keydown', this.handleKeyPress.bind(this));
    }
    
    createOverlay() {
        this.overlay = document.createElement('div');
        this.overlay.className = 'onboarding-overlay';
        this.overlay.innerHTML = `
            <div class="onboarding-progress">
                <div class="onboarding-progress-bar"></div>
            </div>
        `;
        document.body.appendChild(this.overlay);
    }
    
    createTooltip() {
        this.tooltip = document.createElement('div');
        this.tooltip.className = 'onboarding-tooltip';
        this.tooltip.innerHTML = `
            <div class="onboarding-tooltip-arrow"></div>
            <div class="onboarding-tooltip-content">
                <h3 class="onboarding-tooltip-title"></h3>
                <p class="onboarding-tooltip-description"></p>
                <div class="onboarding-tooltip-buttons">
                    <button class="onboarding-btn onboarding-btn-skip">Пропустить</button>
                    <button class="onboarding-btn onboarding-btn-next">Далее →</button>
                </div>
            </div>
        `;
        document.body.appendChild(this.tooltip);
        
        // Добавляем обработчики
        this.tooltip.querySelector('.onboarding-btn-next').addEventListener('click', () => this.next());
        this.tooltip.querySelector('.onboarding-btn-skip').addEventListener('click', () => this.end());
    }
    
    showStep(index) {
        if (index >= this.steps.length) {
            this.end();
            return;
        }
        
        const step = this.steps[index];
        const element = document.querySelector(step.element);
        
        if (!element) {
            // Если элемент не найден, переходим к следующему шагу
            this.next();
            return;
        }
        
        this.currentStep = index;
        
        // Обновляем прогресс
        const progress = ((index + 1) / this.steps.length) * 100;
        document.querySelector('.onboarding-progress-bar').style.width = progress + '%';
        
        // Подсвечиваем элемент
        this.highlightElement(element);
        
        // Обновляем контент тултипа
        this.tooltip.querySelector('.onboarding-tooltip-title').textContent = step.title;
        this.tooltip.querySelector('.onboarding-tooltip-description').textContent = step.description;
        
        // Обновляем текст кнопки
        const nextBtn = this.tooltip.querySelector('.onboarding-btn-next');
        if (index === this.steps.length - 1) {
            nextBtn.textContent = 'Завершить ✨';
        } else {
            nextBtn.textContent = 'Далее →';
        }
        
        // Позиционируем тултип
        this.positionTooltip(element, step.position);
    }
    
    highlightElement(element) {
        // Убираем предыдущую подсветку
        document.querySelectorAll('.onboarding-highlight').forEach(el => {
            el.classList.remove('onboarding-highlight');
        });
        
        // Добавляем подсветку
        element.classList.add('onboarding-highlight');
        
        // Прокручиваем к элементу
        element.scrollIntoView({
            behavior: 'smooth',
            block: 'center'
        });
    }
    
    positionTooltip(element, position) {
        const rect = element.getBoundingClientRect();
        const tooltipRect = this.tooltip.getBoundingClientRect();
        
        let top, left;
        
        switch(position) {
            case 'top':
                top = rect.top - tooltipRect.height - 20;
                left = rect.left + (rect.width / 2) - (tooltipRect.width / 2);
                break;
            case 'bottom':
                top = rect.bottom + 20;
                left = rect.left + (rect.width / 2) - (tooltipRect.width / 2);
                break;
            case 'left':
                top = rect.top + (rect.height / 2) - (tooltipRect.height / 2);
                left = rect.left - tooltipRect.width - 20;
                break;
            case 'right':
                top = rect.top + (rect.height / 2) - (tooltipRect.height / 2);
                left = rect.right + 20;
                break;
        }
        
        // Проверяем, чтобы тултип не выходил за границы экрана
        const maxLeft = window.innerWidth - tooltipRect.width - 20;
        const maxTop = window.innerHeight - tooltipRect.height - 20;
        
        left = Math.max(20, Math.min(left, maxLeft));
        top = Math.max(20, Math.min(top, maxTop));
        
        this.tooltip.style.left = left + 'px';
        this.tooltip.style.top = top + 'px';
        
        // Позиционируем стрелку
        const arrow = this.tooltip.querySelector('.onboarding-tooltip-arrow');
        arrow.className = 'onboarding-tooltip-arrow ' + position;
    }
    
    next() {
        this.showStep(this.currentStep + 1);
    }
    
    end() {
        this.isActive = false;
        this.overlay.remove();
        this.tooltip.remove();
        
        document.querySelectorAll('.onboarding-highlight').forEach(el => {
            el.classList.remove('onboarding-highlight');
        });
        
        document.body.style.overflow = '';
        document.removeEventListener('keydown', this.handleKeyPress);
        
        // Запоминаем, что тур пройден
        localStorage.setItem('onboardingCompleted', 'true');
    }
    
    handleKeyPress(e) {
        if (!this.isActive) return;
        
        if (e.key === 'Escape') {
            this.end();
        } else if (e.key === 'ArrowRight') {
            this.next();
        }
    }
}

document.addEventListener('DOMContentLoaded', () => {
    const tour = new OnboardingTour();
    tour.start();
});
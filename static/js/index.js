window.HELP_IMPROVE_VIDEOJS = false;

// Copy BibTeX to clipboard
function copyBibTeX() {
    const bibtexElement = document.getElementById('bibtex-code');
    const button = document.querySelector('.copy-bibtex-btn');
    const copyText = button.querySelector('.copy-text');
    
    if (bibtexElement) {
        navigator.clipboard.writeText(bibtexElement.textContent).then(function() {
            // Success feedback
            button.classList.add('copied');
            copyText.textContent = 'Copied!';
            
            setTimeout(function() {
                button.classList.remove('copied');
                copyText.textContent = 'Copy';
            }, 2000);
        }).catch(function(err) {
            console.error('Failed to copy: ', err);
            // Fallback for older browsers
            const textArea = document.createElement('textarea');
            textArea.value = bibtexElement.textContent;
            document.body.appendChild(textArea);
            textArea.select();
            document.execCommand('copy');
            document.body.removeChild(textArea);
            
            button.classList.add('copied');
            copyText.textContent = 'Copied!';
            setTimeout(function() {
                button.classList.remove('copied');
                copyText.textContent = 'Copy';
            }, 2000);
        });
    }
}

// Scroll to top functionality
function scrollToTop() {
    window.scrollTo({
        top: 0,
        behavior: 'smooth'
    });
}

// Show/hide scroll to top button
window.addEventListener('scroll', function() {
    const scrollButton = document.querySelector('.scroll-to-top');
    if (!scrollButton) return;

    if (window.pageYOffset > 300) {
        scrollButton.classList.add('visible');
    } else {
        scrollButton.classList.remove('visible');
    }
});

function labelCarouselControls(carousel) {
    const previous = carousel.querySelector('.slider-navigation-previous');
    const next = carousel.querySelector('.slider-navigation-next');

    if (previous) previous.setAttribute('aria-label', 'Previous video comparison');
    if (next) next.setAttribute('aria-label', 'Next video comparison');
}

function labelCarouselPagination(carousel) {
    carousel.querySelectorAll('.slider-pagination .slider-page').forEach((page, index) => {
        page.setAttribute('aria-label', `Show video comparison ${index + 1}`);
    });
}

function getVisibleCarouselItem(carousel) {
    const viewportCenter = window.innerWidth / 2;
    const visibleItems = Array.from(carousel.querySelectorAll('.slider-item')).filter(item => {
        const rect = item.getBoundingClientRect();
        return rect.right > 0 && rect.left < window.innerWidth;
    });

    return visibleItems.reduce((closestItem, item) => {
        const itemRect = item.getBoundingClientRect();
        const itemDistance = Math.abs((itemRect.left + itemRect.right) / 2 - viewportCenter);

        if (!closestItem) return item;

        const closestRect = closestItem.getBoundingClientRect();
        const closestDistance = Math.abs((closestRect.left + closestRect.right) / 2 - viewportCenter);
        return itemDistance < closestDistance ? item : closestItem;
    }, null);
}

function pauseHiddenCarouselVideos(carousel) {
    const visibleItem = getVisibleCarouselItem(carousel);

    carousel.querySelectorAll('video').forEach(video => {
        if (!visibleItem || !visibleItem.contains(video)) {
            video.pause();
        }
    });
}

function playVisibleCarouselVideos(carousel) {
    const visibleItem = getVisibleCarouselItem(carousel);
    if (!visibleItem) return;

    visibleItem.querySelectorAll('video').forEach(video => {
        video.play().catch(() => {
            // Browsers can reject autoplay; controls remain available for manual playback.
        });
    });
}

function updateCarouselVideoPlayback(carousel) {
    pauseHiddenCarouselVideos(carousel);
    playVisibleCarouselVideos(carousel);
}

function isMediaControlEvent(event) {
    return Boolean(event.target.closest('video'));
}

function observeCarouselChanges(carousel) {
    const sliderContainer = carousel.querySelector('.slider-container');
    if (!sliderContainer) return;

    const observer = new MutationObserver(() => updateCarouselVideoPlayback(carousel));
    observer.observe(sliderContainer, {
        attributes: true,
        attributeFilter: ['class', 'style'],
        subtree: true,
    });
}

function setupResultsCarousel() {
    if (typeof bulmaCarousel === 'undefined') return;

    bulmaCarousel.attach('.carousel', {
        slidesToScroll: 1,
        slidesToShow: 1,
        loop: true,
        infinite: true,
        autoplay: false,
    });

    document.querySelectorAll('.carousel').forEach(carousel => {
        labelCarouselControls(carousel);
        labelCarouselPagination(carousel);
        updateCarouselVideoPlayback(carousel);
        observeCarouselChanges(carousel);
        carousel.addEventListener('click', event => {
            if (!isMediaControlEvent(event)) {
                setTimeout(() => updateCarouselVideoPlayback(carousel), 350);
            }
        });
        carousel.addEventListener('keydown', event => {
            if (!isMediaControlEvent(event)) {
                setTimeout(() => updateCarouselVideoPlayback(carousel), 350);
            }
        });
    });
}

document.addEventListener('DOMContentLoaded', setupResultsCarousel);


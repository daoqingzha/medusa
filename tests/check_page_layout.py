from html.parser import HTMLParser
from pathlib import Path


class PageParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tags = []
        self.text_parts = []
        self.images = []
        self.videos = []
        self.sources = []

    def handle_starttag(self, tag, attrs):
        attr = dict(attrs)
        self.tags.append((tag, attr))
        if tag == "img":
            self.images.append(attr)
        if tag == "video":
            self.videos.append(attr)
        if tag == "source":
            self.sources.append(attr)

    def handle_data(self, data):
        text = data.strip()
        if text:
            self.text_parts.append(text)


def class_tokens(attrs):
    return set(attrs.get("class", "").split())


PROJECT_ROOT = Path(__file__).resolve().parents[1]


html = (PROJECT_ROOT / "index.html").read_text()
parser = PageParser()
parser.feed(html)
page_text = "\n".join(parser.text_parts)
compact_text = " ".join(parser.text_parts)

assert "Method & Analysis" in page_text, "Expected Method & Analysis section heading"
assert "* Equal Contribution · † Corresponding Author" in compact_text, "Author notes should be a single concise line"
assert "Indicates Equal Contribution" not in page_text, "Author notes should not use inconsistent Indicates wording"
assert 'id="results-carousel" class="carousel results-carousel"' in html, "Expected template-style Bulma results carousel"
assert "bulma-carousel.min.css" in html, "Carousel should load Bulma carousel CSS like the reference page"
assert "bulma-carousel.min.js" in html, "Carousel should load Bulma carousel JavaScript like the reference page"
assert "bulma-slider" not in html, "Slider assets should not load when no sliders are used"
assert "jquery" in html.lower(), "Bulma carousel template should load jQuery like the reference page"
assert "This page was built using" not in page_text, "Template/copyright footer credit should be removed"
assert not any(tag == "footer" for tag, _ in parser.tags), "Footer element should be removed"
assert "  title     = {MEDUSA: Motion Elimination in Diffusion Using Spectral Attack}," in html, "BibTeX title field should align equals signs"
assert "  author    = {Yu, Hongwei and Zha, Daoqing and Ding, Xinlong and Li, Jiawei and Zhuo, Junbao and Liu, Qiankun and Ma, Huimin and Chen, Jiansheng}," in html, "BibTeX author field should align equals signs"
assert "  booktitle = {Proceedings of the International Conference on Machine Learning}," in html, "BibTeX booktitle field should align equals signs"
assert "  year      = {2026}" in html, "BibTeX year field should align equals signs"

expected_images = {
    "static/images/result-attention-spectrum.png",
    "static/images/result-loss-comparison.png",
    "static/images/result-qualitative-comparison.png",
}
actual_images = {attrs.get("src") for attrs in parser.images}
missing = expected_images - actual_images
assert not missing, f"Missing inline analysis images: {sorted(missing)}"

loss_images = [attrs for attrs in parser.images if attrs.get("src") == "static/images/result-loss-comparison.png"]
assert loss_images, "Expected loss comparison image"
assert "analysis-figure--narrow" in class_tokens(loss_images[0]), "Loss figure should use constrained-width class"

css = (PROJECT_ROOT / "static/css/index.css").read_text()
assert ".analysis-figure--narrow" in css, "Expected CSS rule for constrained loss figure"
assert "max-width: 560px" in css, "Loss figure max-width should be constrained to 560px"
for caption in [
    "This analysis connects the visual attention pattern to the singular-value distribution",
    "The optimization curve highlights why the spectral objective is easier to optimize",
    "These qualitative examples illustrate that MEDUSA can impose motion-suppressing perturbations",
]:
    assert caption in page_text, f"Missing enriched caption text: {caption}"

expected_video_groups = ["02", "03", "04", "05", "06", "07"]
assert "Result" in page_text, "Carousel section should use the concise Result heading"
assert "Clean vs. MEDUSA Attack" not in page_text, "Carousel should not use the longer comparison heading"
assert "Each carousel page compares" not in page_text, "Carousel intro copy should be removed"
for video_id in expected_video_groups:
    assert f'data-video-group="{video_id}"' in html, f"Missing carousel item for example {video_id}"
    assert f"static/videos/clean/{video_id}.mp4" in html, f"Missing clean video for example {video_id}"
    assert f"static/videos/attack/{video_id}.mp4" in html, f"Missing attacked video for example {video_id}"
    assert f'aria-label="Example {video_id} clean generation video"' in html, f"Missing accessible clean video label for example {video_id}"
    assert f'aria-label="Example {video_id} MEDUSA attack video"' in html, f"Missing accessible attack video label for example {video_id}"
    assert f"Example {video_id}:" not in page_text, f"Per-slide caption should be removed for example {video_id}"

assert len(parser.videos) >= len(expected_video_groups) * 2, "Each carousel slide should include clean and attacked videos"
assert "Clean generation" in page_text, "Carousel should label un-attacked videos"
assert "MEDUSA attack" in page_text, "Carousel should label attacked videos"
assert ".results-carousel .item" in css, "Expected CSS for template-style results carousel items"
assert ".video-pair" in css, "Expected CSS for two-video comparison layout"
js = (PROJECT_ROOT / "static/js/index.js").read_text()
assert "bulmaCarousel.attach('.carousel'" in js, "Expected Bulma carousel initialization"
assert "setupVideoComparisonCarousel" not in js, "Custom carousel JavaScript should be removed"
assert "labelCarouselControls" in js, "Generated carousel controls should receive accessible labels"
assert "pauseHiddenCarouselVideos" in js, "Hidden carousel videos should pause after slide changes"
assert "labelCarouselPagination" in js, "Generated carousel pagination should receive accessible labels"
assert "observeCarouselChanges" in js, "Carousel should pause hidden videos after plugin-driven slide changes"
assert "MutationObserver" in js, "Carousel should observe class/style changes from click, keyboard, or drag navigation"
assert "querySelectorAll('video')" in js, "Carousel video pause logic should target video elements"
assert "getVisibleCarouselItem" in js, "Autoplay should choose the slide visibly centered in the viewport"
assert "getBoundingClientRect" in js, "Visible slide detection should use rendered slide positions"
assert "window.innerWidth / 2" in js, "Visible slide detection should compare slides against viewport center"
assert "playVisibleCarouselVideos" in js, "Visible carousel videos should autoplay after slide changes"
assert ".play()" in js, "Autoplay logic should call play on visible videos"
assert "catch" in js, "Autoplay logic should tolerate browser autoplay rejection"
assert "isMediaControlEvent" in js, "Carousel resync should ignore direct video/media-control interactions"
assert "event.target.closest('video')" in js, "Carousel click handling should not restart user-paused videos"
assert "Your browser does not support the video tag." in html, "Videos should include fallback text"

for src in expected_images | {"static/images/medusa-overview-hd.png"}:
    assert (PROJECT_ROOT / src).exists(), f"Referenced image file does not exist: {src}"
for video_id in expected_video_groups:
    for state in ["clean", "attack"]:
        src = PROJECT_ROOT / f"static/videos/{state}/{video_id}.mp4"
        assert src.exists(), f"Referenced video file does not exist: {src}"

print("Page layout check passed")

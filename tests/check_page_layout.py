from html.parser import HTMLParser
from pathlib import Path


class PageParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tags = []
        self.text_parts = []
        self.images = []

    def handle_starttag(self, tag, attrs):
        attr = dict(attrs)
        self.tags.append((tag, attr))
        if tag == "img":
            self.images.append(attr)

    def handle_data(self, data):
        text = data.strip()
        if text:
            self.text_parts.append(text)


def class_tokens(attrs):
    return set(attrs.get("class", "").split())


html = Path("index.html").read_text()
parser = PageParser()
parser.feed(html)
page_text = "\n".join(parser.text_parts)
compact_text = " ".join(parser.text_parts)

assert "Method & Analysis" in page_text, "Expected Method & Analysis section heading"
assert "* Equal Contribution · † Corresponding Author" in compact_text, "Author notes should be a single concise line"
assert "Indicates Equal Contribution" not in page_text, "Author notes should not use inconsistent Indicates wording"
assert "results-carousel" not in html, "Static analysis figures should not be inside carousel markup"
assert "bulma-carousel" not in html, "Carousel assets should not load after removing carousel markup"
assert "bulma-slider" not in html, "Slider assets should not load when no sliders are used"
assert "jquery" not in html.lower(), "jQuery should not load when page scripts do not use it"
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

css = Path("static/css/index.css").read_text()
assert ".analysis-figure--narrow" in css, "Expected CSS rule for constrained loss figure"
assert "max-width: 560px" in css, "Loss figure max-width should be constrained to 560px"
for caption in [
    "This analysis connects the visual attention pattern to the singular-value distribution",
    "The optimization curve highlights why the spectral objective is easier to optimize",
    "These qualitative examples illustrate that MEDUSA can impose motion-suppressing perturbations",
]:
    assert caption in page_text, f"Missing enriched caption text: {caption}"

for src in expected_images | {"static/images/medusa-overview-hd.png"}:
    assert Path(src).exists(), f"Referenced image file does not exist: {src}"

print("Page layout check passed")

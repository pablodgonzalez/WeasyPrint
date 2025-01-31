"""
    weasyprint.svg.image
    --------------------

    Draw image and svg tags.

"""

from urllib.parse import urljoin

from .utils import preserve_ratio


def svg(svg, node, font_size):
    """Draw svg tags."""
    x, y = svg.point(node.get('x'), node.get('y'), font_size)
    svg.stream.transform(e=x, f=y)
    if svg.tree == node:
        width, height = svg.concrete_width, svg.concrete_height
    else:
        width, height = svg.point(
            node.get('width'), node.get('height'), font_size)
    scale_x, scale_y, translate_x, translate_y = preserve_ratio(
        svg, node, font_size, width, height)
    if svg.tree != node:
        svg.stream.rectangle(0, 0, width, height)
        svg.stream.clip()
        svg.stream.end()
    svg.stream.transform(a=scale_x, d=scale_y, e=translate_x, f=translate_y)


def image(svg, node, font_size):
    """Draw image tags."""
    x, y = svg.point(node.get('x'), node.get('y'), font_size)
    svg.stream.transform(e=x, f=y)
    base_url = node.get('{http://www.w3.org/XML/1998/namespace}base')
    url = urljoin(base_url or svg.url, node.get_href())
    image = svg.context.get_image_from_uri(url=url, forced_mime_type='image/*')
    if image is None:
        return

    width, height = svg.point(node.get('width'), node.get('height'), font_size)
    intrinsic_width, intrinsic_height, intrinsic_ratio = (
        image.get_intrinsic_size(1, font_size))
    if intrinsic_width is None and intrinsic_height is None:
        if intrinsic_ratio is None or (not width and not height):
            intrinsic_width, intrinsic_height = 300, 150
        elif not width:
            intrinsic_width, intrinsic_height = (
                intrinsic_ratio * height, height)
        else:
            intrinsic_width, intrinsic_height = width, width / intrinsic_ratio
    elif intrinsic_width is None:
        intrinsic_width = intrinsic_ratio * intrinsic_height
    elif intrinsic_height is None:
        intrinsic_height = intrinsic_width / intrinsic_ratio
    width = width or intrinsic_width
    height = height or intrinsic_height

    scale_x, scale_y, translate_x, translate_y = preserve_ratio(
        svg, node, font_size, width, height,
        (0, 0, intrinsic_width, intrinsic_height))
    svg.stream.rectangle(0, 0, width, height)
    svg.stream.clip()
    svg.stream.end()
    svg.stream.push_state()
    svg.stream.transform(a=scale_x, d=scale_y, e=translate_x, f=translate_y)
    image.draw(
        svg.stream, intrinsic_width, intrinsic_height, image_rendering='auto')
    svg.stream.pop_state()

#!/usr/bin/env python
# vim:fileencoding=UTF-8:ts=4:sw=4:sta:et:sts=4:ai
from __future__ import with_statement

__license__   = 'GPL v3'
__copyright__ = '2009, Kovid Goyal <kovid@kovidgoyal.net>'
__docformat__ = 'restructuredtext en'

import sys
from xml.sax.saxutils import escape
from itertools import repeat

from lxml import etree

from calibre import guess_type, strftime
from calibre.constants import __appname__, __version__
from calibre.ebooks.BeautifulSoup import BeautifulSoup
from calibre.ebooks.oeb.base import XPath, XHTML_NS, XHTML
from calibre.library.comments import comments_to_html
from calibre.utils.magick.draw import save_cover_data_to

JACKET_XPATH = '//h:meta[@name="calibre-content" and @content="jacket"]'

class Jacket(object):
    '''
    Book jacket manipulation. Remove first image and insert comments at start of
    book.
    '''

    def remove_images(self, item, limit=1):
        path = XPath('//h:img[@src]')
        removed = 0
        for img in path(item.data):
            if removed >= limit:
                break
            href  = item.abshref(img.get('src'))
            image = self.oeb.manifest.hrefs.get(href, None)
            if image is not None:
                self.oeb.manifest.remove(image)
                img.getparent().remove(img)
                removed += 1
        return removed

    def remove_first_image(self):
        for item in self.oeb.spine:
            removed = self.remove_images(item)
            if removed > 0:
                self.log('Removed first image')
                break

    def insert_metadata(self, mi):
        self.log('Inserting metadata into book...')

        fname = 'star.png'
        img = I(fname, data=True)

        if self.opts.output_profile.short_name == 'kindle':
            fname = 'star.jpg'
            img = save_cover_data_to(img, fname,
                return_data=True)


        id, href = self.oeb.manifest.generate('calibre_jacket_star', fname)
        self.oeb.manifest.add(id, href, guess_type(fname)[0], data=img)

        try:
            tags = map(unicode, self.oeb.metadata.subject)
        except:
            tags = []

        root = render_jacket(mi, self.opts.output_profile, star_href=href,
                alt_title=unicode(self.oeb.metadata.title[0]), alt_tags=tags,
                alt_comments=unicode(self.oeb.metadata.description[0]))
        id, href = self.oeb.manifest.generate('calibre_jacket', 'jacket.xhtml')

        item = self.oeb.manifest.add(id, href, guess_type(href)[0], data=root)
        self.oeb.spine.insert(0, item, True)

    def remove_existing_jacket(self):
        for x in self.oeb.spine[:4]:
            if XPath(JACKET_XPATH)(x.data):
                self.remove_images(x, limit=sys.maxint)
                self.oeb.manifest.remove(x)
                break

    def __call__(self, oeb, opts, metadata):
        '''
        Add metadata in jacket.xhtml if specified in opts
        If not specified, remove previous jacket instance
        '''
        self.oeb, self.opts, self.log = oeb, opts, oeb.log
        self.remove_existing_jacket()
        if opts.remove_first_image:
            self.remove_first_image()
        if opts.insert_metadata:
            self.insert_metadata(metadata)

# Render Jacket {{{

def get_rating(rating, href):
    ans = ''
    try:
        num = float(rating)/2
    except:
        return ans
    num = max(0, num)
    num = min(num, 5)
    if num < 1:
        return ans

    if href is not None:
        ans = ' '.join(repeat(
            '<img style="vertical-align:text-bottom" alt="star" src="%s" />'%
            href, int(num)))
    else:
        ans = u' '.join(u'\u2605')
    return ans


def render_jacket(mi, output_profile, star_href=None,
        alt_title=_('Unknown'), alt_tags=[], alt_comments=''):
    css = P('jacket/stylesheet.css', data=True).decode('utf-8')

    try:
        title_str = mi.title if mi.title else alt_title
    except:
        title_str = _('Unknown')
    title = '<span class="title">%s</span>' % (escape(title_str))

    series = escape(mi.series if mi.series else '')
    if mi.series and mi.series_index is not None:
        series += escape(' [%s]'%mi.format_series_index())
    if not mi.series:
        series = ''

    try:
        pubdate = strftime(u'%Y', mi.pubdate.timetuple())
    except:
        pubdate = ''

    rating = get_rating(mi.rating, star_href)

    tags = mi.tags if mi.tags else alt_tags
    if tags:
        tags = output_profile.tags_to_string(tags)
    else:
        tags = ''

    comments = mi.comments if mi.comments else alt_comments
    comments = comments.strip()
    orig_comments = comments
    if comments:
        comments = comments_to_html(comments)

    footer = 'B<span class="cbj_smallcaps">OOK JACKET GENERATED BY %s %s</span>' % (__appname__.upper(),__version__)

    def generate_html(comments):
        args = dict(xmlns=XHTML_NS,
                    title_str=title_str,
                    css=css,
                    title=title,
                    pubdate_label=_('Published'), pubdate=pubdate,
                    series_label=_('Series'), series=series,
                    rating_label=_('Rating'), rating=rating,
                    tags_label=_('Tags'), tags=tags,
                    comments=comments,
                    footer = footer)

        generated_html = P('jacket/template.xhtml',
                data=True).decode('utf-8').format(**args)

        # Post-process the generated html to strip out empty header items
        soup = BeautifulSoup(generated_html)
        if not series:
            series_tag = soup.find('tr', attrs={'class':'cbj_series'})
            series_tag.extract()
        if not rating:
            rating_tag = soup.find('tr', attrs={'class':'cbj_rating'})
            rating_tag.extract()
        if not tags:
            tags_tag = soup.find('tr', attrs={'class':'cbj_tags'})
            tags_tag.extract()
        if not pubdate:
            pubdate_tag = soup.find('tr', attrs={'class':'cbj_pubdate'})
            pubdate_tag.extract()
        if output_profile.short_name != 'kindle':
            hr_tag = soup.find('hr', attrs={'class':'cbj_kindle_banner_hr'})
            hr_tag.extract()

        return soup.renderContents(None)

    from calibre.ebooks.oeb.base import RECOVER_PARSER

    try:
        root = etree.fromstring(generate_html(comments), parser=RECOVER_PARSER)
    except:
        try:
            root = etree.fromstring(generate_html(escape(orig_comments)),
                parser=RECOVER_PARSER)
        except:
            root = etree.fromstring(generate_html(''),
                parser=RECOVER_PARSER)
    return root

# }}}

def linearize_jacket(oeb):
    for x in oeb.spine[:4]:
        if XPath(JACKET_XPATH)(x.data):
            for e in XPath('//h:table|//h:tr|//h:th')(x.data):
                e.tag = XHTML('div')
            for e in XPath('//h:td')(x.data):
                e.tag = XHTML('span')
            break


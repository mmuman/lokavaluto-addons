# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import json

from odoo import http
from odoo.http import request
from odoo.tools import html_escape as escape

class LeafletMap(http.Controller):
    '''
    This class generates on-the-fly partner maps that can be reused in every
    website page. To do so, just use an ``<iframe ...>`` whose ``src``
    attribute points to ``/leaflet_map`` (this controller generates a complete
    HTML5 page).

    URL query parameters:
    - ``partner_ids``: a comma-separated list of ids (partners to be shown)
    - ``partner_url``: the base-url to display the partner
        (eg: if ``partner_url`` is ``/partners/``, when the user will click on
        a partner on the map, it will be redirected to <myodoo>.com/partners/<id>)

    In order to resize the map, simply resize the ``iframe`` with CSS
    directives ``width`` and ``height``.
    '''

    @http.route(['/leaflet_map'], type='http', auth='public', website=True)
    def leaflet_map(self, *arg, **post):
        clean_ids = []
        search_domain = []
        try:
            for partner_id in post.get('partner_ids', "").split(","):
                clean_ids.append(int(partner_id))
            if len(clean_ids):
                search_domain.append(("id", "in", clean_ids))
        #except ValueError:
        except Exception:
            pass
        search_domain.extend([('website_published', '=', True), ('is_company', '=', True)])
        partners = request.env['res.partner'].search(search_domain)
        partner_data = {
            "counter": len(partners),
            "partners": []
        }
        for partner in partners.with_context({'show_address': True}):
            # TODO in master, do not use `escape` but `t-esc` in the qweb template.
            # TODO make sure they are all geolocalized already
            partner_data["partners"].append({
                'id': partner.id,
                'name': escape(partner.name),
                'address': escape('\n'.join(partner.name_get()[0][1].split('\n')[1:])),
                'latitude': escape(str(partner.partner_latitude)),
                'longitude': escape(str(partner.partner_longitude)),
            })
        if 'customers' in post.get('partner_url', ''):
            partner_url = '/customers/'
        else:
            partner_url = '/partners/'

        values = {
            'partner_url': partner_url,
            'partner_data': json.dumps(partner_data),
        }
        return request.render("website_leaflet_map.leaflet_map", values)

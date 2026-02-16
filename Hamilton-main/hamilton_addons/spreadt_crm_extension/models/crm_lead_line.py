from odoo import models,fields,api
from odoo.exceptions import UserError


class CrmLeadLine(models.Model):
    _name = "crm.lead.line"
    _description = 'CRM lead lines for Quote'

    @api.multi
    @api.depends('quoted_price', 'quantity')
    def _get_total_price(self):
        sub_total = 0.0
        for rec in self:
            rec.total_price = rec.quoted_price * rec.quantity

    product_id = fields.Many2one("product.product","Product")
    quantity = fields.Float("Quantity", default=1)
    quoted_price = fields.Float("Quoted Price")
    crm_lead_id = fields.Many2one("crm.lead","Lead")
    uom_id = fields.Many2one('uom.uom', string='Unit of Measure')
    total_price = fields.Float(string='Total', compute='_get_total_price',
                               store=True)
    #price_category_id = fields.Many2one('price.category', required=True)

    @api.onchange('product_id')
    def onchange_product_id(self):
        '''
        Change UOM and price of product based on product
        :return:
        '''
        if self.product_id and self.product_id.lst_price and \
                self.product_id.uom_id:
            self.uom_id = self.product_id.uom_id.id
            res = self.product_id.lst_price
            if not self.crm_lead_id.price_category_id:
                raise UserError("Please select the price category !")
            if self.crm_lead_id.price_category_id.percentage > 0.0 and self.crm_lead_id.price_category_id.percentage < 100.0:
                minus_price = self.product_id.msrp * ((self.crm_lead_id.price_category_id.percentage or 0.0) / 100.0)
                res = self.product_id.msrp - minus_price
            if self.crm_lead_id.price_category_id.percentage >= 100.0:
                res = self.product_id.msrp
            self.quoted_price = res



class CrmLead(models.Model):
    _inherit = "crm.lead"

    crm_lead_line_ids = fields.One2many("crm.lead.line","crm_lead_id","Lines")
    price_category_id = fields.Many2one('price.category')

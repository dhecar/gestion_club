# -*- encoding= utf-8 -*-

from openerp import fields,models,api
import datetime
import time
from openerp.exceptions	import	ValidationError

STATE = [('actif','Actif'),('inactif','Inactif')]
class adherent_adherent(models.Model):
	_name = "adherent.adherent"
	_description= "adherent"

	cin = fields.Char(string="cin",size=50,required=True)
	name = fields.Char(string="nom",size=50,required=True)
	prenom = fields.Char(string="prenom",size=50,required=True)
	age  = fields.Integer(string="age")
	adresse = fields.Char(string="adresse",size=100)
	telephone = fields.Char(string="telephone",size=100,required=True)
	photo = fields.Binary("photo")
	sexe = fields.Selection([('homme','Homme'),('femme','Femme')],"sexe",  default="homme")
	inscription =fields.One2many("insc.insc","adh_id","Les abonnements")
	point = fields.One2many("point.point","adh_id","Pointage")
	
	nbr_insc = fields.Integer(string="le nombre d'inscription",compute='insc_count', readonly=True)
	total = fields.Float(string='le total',store=True, readonly=True, compute='_compute_total')
	paye = fields.Float(string='le montant payé',store=True, readonly=True, compute='_compute_paye')
	reste_tarif = fields.Float(string='le reste',store=True, readonly=True, compute='_compute_reste')
	etat  =  fields.Selection(STATE , "etat" , readonly=False,default='actif')
	color = fields.Integer('Color Index', compute="change_colore_on_kanban")
	
	_rec_name = 'name'

	@api.multi
	def change_colore_on_kanban(self):
		for record in self:
			print 'record :',record
			c = 0
			if record.etat == 'inactif':
				record.color = 2
			elif record.etat == 'actif':
				record.color = 5
			print ' c : ',record.color

	@api.model
	def create(self,vals):
		if 'cin' in vals:
			vals['cin']=vals['cin'].upper()
		return super(adherent_adherent, self).create(vals)

	@api.multi
	def write(self,vals):
		if 'cin' in vals:
			for rec in self:
				vals['cin']=vals['cin'].upper()
		return super(adherent_adherent, self).write(vals)


	@api.one
	@api.depends('inscription.tarif')
	def _compute_paye(self):
		self.paye = sum(line.tarif - line.reste for line in self.inscription if line.etat==True)

	@api.one
	@api.depends('inscription.reste')
	def _compute_reste(self):
		self.reste_tarif = sum(line.reste for line in self.inscription)


	@api.one
	@api.depends('inscription.tarif')
	def _compute_total(self):
		self.total = sum(line.tarif for line in self.inscription if line.etat==True)
		

	@api.one
	def	insc_count(self):
		self.nbr_insc = self.env['insc.insc'].search_count([('adh_id','=', self.id)])
		print self.nbr_insc

	@api.multi
	def unlink(self):
		for rec in self:
			ins = self.env['insc.insc'].search([('adh_id','=', rec.id)])
			print 'ins :',ins
			point = self.env['point.point'].search([('adh_id','=', rec.id)])
			print 'point :',point
			for j in point:
				j.unlink()
			for i in ins:
				i.unlink()
		return super(adherent_adherent, self).unlink()

	


class insc_insc(models.Model):
	_name = "insc.insc"
	_description= "inscription"

	date_debut = fields.Date(string="date de debut", required = True)
	date_fin = fields.Date(string="date de fin", required = True)
	adh_id = fields.Many2one("adherent.adherent", "l'adherent",required=True, Ondelete="cascade")
	act_id = fields.Many2one("activite.activite", "l'activite",required=True, Ondelete="cascade")
	tarif =fields.Float(string='tarif', store=True, related='act_id.tarif', readonly=True)
	etat = fields.Boolean("etat",default=True)
	reste =fields.Float("reste" , default= 0.0)
	point = fields.One2many("point.point","insc_id","Pontage")
	tarif_actif = fields.Float(string='le tarif',store=True, readonly=True, compute='_compute_tarif_actif')

	_rec_name = 'act_id'
	

	@api.one
	@api.depends('tarif','date_fin')
	def _compute_tarif_actif(self):
		if self.etat == True:
			self.tarif_actif = self.tarif - self.reste
		else:
			self.tarif_actif = 0

	@api.model
	def update_s(self):
		rec = self.search([('date_fin', '<', datetime.date.today())])
		print 'rec : ',rec
		for r in rec:
			# if r.etat == True:
			print 'r : ',r
			r.write({'etat':False,'date_fin':r.date_fin})


	@api.multi
	def write(self,vals):
		for rec in self:
			adh = rec.adh_id
			if 'date_fin' in vals:
				if vals['date_fin'] >= time.strftime("%Y-%m-%d"):
					vals['etat']=True
					adh.write({'etat':'actif'})
				else:
					vals['etat']=False
					adh.write({'etat':'inactif'})
					for inscs in adh.inscription:
						if inscs.etat == True and inscs != rec:
							adh.write({'etat':'actif'})
			return super(insc_insc, self).write(vals)

	@api.model
	def create(self,vals):
		adh = self.env['adherent.adherent'].search([('id','=', vals['adh_id'])])
		adh.write({'etat':'actif'})
		return super(insc_insc, self).create(vals)


	@api.multi
	@api.depends('adh_id', 'act_id')
	def name_get(self):
		result = []
		for record in self:
			result.append((record.id, "%s -> %s" % (record.adh_id.name, record.act_id.nom)))
		return result





class activite_activite(models.Model):
	_name = 'activite.activite'
	_description= "activite"

	nom = fields.Char(string="le nom",size=40,required=True)
	inscription = fields.One2many("insc.insc","act_id","les inscription")
	tarif =fields.Float("Tarif",required=True)
	_rec_name = 'nom'


	



class point_point(models.Model):
	_name = "point.point"
	_description= "Pointage"
	
	date = fields.Date(string="date", required = True)
	adh_id = fields.Many2one("adherent.adherent", "l'adherent",required=True, Ondelete="cascade")
	insc_id = fields.Many2one("insc.insc", "l'abonnement",required=True,Ondelete="cascade")


	@api.onchange('adh_id')
	def _onchange_adh(self):
		rec = self.env['insc.insc'].search([('adh_id','=', self.adh_id.id),('etat','=',True)])
		return {'domain':{'insc_id':[('id','in',rec.ids)]}}

	






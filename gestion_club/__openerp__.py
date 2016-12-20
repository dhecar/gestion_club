# -*- coding: utf-8 -*-
{
        "name" : "club",
        "version" : "1.1",
        "author" : "Mohamed Charif EL HARTI",
        "category" : "Gestion Sport",
        "description": """ 
	application pour la gestion des salles de sport
	""",
        "depends" : ['report','web_kanban','base_setup', 'board', 'edi'],

        "data" : [
        'security/club_security.xml',
        'security/ir.model.access.csv',
        'club.xml',
        'workflow/workflow.xml',
        'data/scheduler_data.xml',
        'views/report_adh.xml',
        'adherent_report.xml'],

    
        'installable': True,
        'auto_install': False,
        'application': True,
}


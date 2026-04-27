import os
import shutil
from datetime import datetime
import openpyxl
from openpyxl.styles import Font, Border, Side, Alignment
from config.settings import OUTPUT_DIR, TEMPLATES_DIR

def generate_excel_bom(config, bom_items):
    """Génère un fichier Excel BOM basé sur le template client."""
    template_path = os.path.join(TEMPLATES_DIR, "BOM_1.xlsx")
    filename = f"BOM_{config.get('client_nom', 'client')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    output_path = os.path.join(OUTPUT_DIR, filename)
    
    # Copier le template
    shutil.copy(template_path, output_path)
    
    # Charger le classeur
    wb = openpyxl.load_workbook(output_path)
    ws = wb.active # Feuil1
    
    # Remplir les données (Exemple basé sur l'inspection)
    # A2: CIMELTA (Nom de l'entreprise peut-être ?)
    # On commence à insérer les items à partir de la ligne 4
    
    start_row = 4
    for i, item in enumerate(bom_items):
        row = start_row + i
        # Si on dépasse les lignes existantes, on peut avoir besoin d'insérer des lignes ou juste écrire
        # Pour rester simple et garder le formatage du SUB-TOTAL à la fin, on pourrait insérer des lignes
        if row >= 12: # Ligne du sub-total originale
            ws.insert_rows(row)
            
        ws.cell(row=row, column=1).value = f"1.{i+1}" # A: #
        ws.cell(row=row, column=2).value = item.get('marque', '') + " " + item.get('modele', '') # B: Code/Model
        ws.cell(row=row, column=4).value = item.get('designation', '') # D: Description
        ws.cell(row=row, column=8).value = "Unit" # H: Unit
        ws.cell(row=row, column=9).value = item.get('quantite', 1) # I: Qty
        ws.cell(row=row, column=11).value = 0 # K: Discount
        ws.cell(row=row, column=12).value = item.get('prix_unitaire', 0) # L: Unit Price
        # M: Amount est souvent une formule dans Excel, mais on peut l'écrire
        ws.cell(row=row, column=13).value = item.get('quantite', 1) * item.get('prix_unitaire', 0)

    wb.save(output_path)
    return output_path

def generate_excel_sow(config, sow_content, bom_items=None):
    """Génère un fichier Excel SOW basé sur le template client."""
    template_path = os.path.join(TEMPLATES_DIR, "SOW_1.xlsx")
    filename = f"SOW_{config.get('client_nom', 'client')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    output_path = os.path.join(OUTPUT_DIR, filename)
    
    # Copier le template
    shutil.copy(template_path, output_path)
    
    # Charger le classeur
    wb = openpyxl.load_workbook(output_path)
    ws = wb["SoW"]
    
    # Remplir les informations de base
    ws["D10"] = config.get('client_nom', 'N/A')
    ws["D12"] = config.get('site_intervention', 'Antananarivo')
    ws["D13"] = config.get('projet_description', '')
    
    # Remplir les tâches à partir de la ligne 20
    taches = sow_content.get('taches', [])
    start_row = 20
    
    # Supprimer les lignes d'exemple si nécessaire ou juste écraser
    # On va insérer les nouvelles tâches
    for i, t in enumerate(taches):
        row = start_row + i
        if i > 0: # On insère pour décaler les commentaires et le récap
            ws.insert_rows(row)
            
        ws.cell(row=row, column=2).value = f"Phase {t.get('phase_num', 1)}" # B: Phase
        ws.cell(row=row, column=3).value = t.get('type', 'Implémentation') # C: Type
        ws.cell(row=row, column=4).value = t.get('titre', '') # D: Tâche
        ws.cell(row=row, column=5).value = t.get('description', '') # E: Description
        ws.cell(row=row, column=6).value = config.get('site_intervention', 'Client Site') # F: Site
        ws.cell(row=row, column=7).value = "Ing-1" # G: Difficulté/Role
        ws.cell(row=row, column=8).value = 1 # H: Nb intervenants
        ws.cell(row=row, column=9).value = t.get('duree_jours', 1) # I: Durée
        
        # Appliquer un alignement wrap text pour la description
        ws.cell(row=row, column=5).alignment = Alignment(wrapText=True, vertical='top')

    wb.save(output_path)
    return output_path

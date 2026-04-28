import os
import shutil
from datetime import datetime
import openpyxl
from openpyxl.styles import Font, Border, Side, Alignment, PatternFill
from config.settings import OUTPUT_DIR, TEMPLATES_DIR

def copy_cell_style(source_cell, target_cell):
    """Copie le style complet d'une cellule vers une autre."""
    if source_cell.has_style:
        target_cell.font = source_cell.font.copy()
        target_cell.border = source_cell.border.copy()
        target_cell.fill = source_cell.fill.copy()
        target_cell.number_format = source_cell.number_format
        target_cell.protection = source_cell.protection.copy()
        target_cell.alignment = source_cell.alignment.copy()

def apply_magenta_style(cell, bold=False, align='center', font_size=10):
    """Applique le style magenta (bordures et police) aux cellules."""
    magenta = "B01B6B"
    cell.font = Font(name='Calibri', size=font_size, bold=bold, color=magenta)
    cell.alignment = Alignment(horizontal=align, vertical='center', wrap_text=True)
    
    magenta_side = Side(style='thin', color=magenta)
    cell.border = Border(left=magenta_side, right=magenta_side, top=magenta_side, bottom=magenta_side)

def safe_write(ws, row, col, value):
    """Écrit une valeur dans une cellule, en gérant les cellules fusionnées."""
    cell = ws.cell(row=row, column=col)
    if isinstance(cell, openpyxl.cell.cell.MergedCell):
        for merged_range in ws.merged_cells.ranges:
            if cell.coordinate in merged_range:
                ws.cell(row=merged_range.min_row, column=merged_range.min_col).value = value
                return
    else:
        cell.value = value

def generate_excel_bom(config, bom_items):
    """Remplit le template Excel BOM_1.xlsx avec une mise en page type CIMELTA."""
    template_path = os.path.join(TEMPLATES_DIR, "BOM_1.xlsx")
    filename = f"BOM_{config.get('client_nom', 'client')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    output_path = os.path.join(OUTPUT_DIR, filename)
    
    if not os.path.exists(template_path):
        wb = openpyxl.Workbook()
        ws = wb.active
        return generate_bom_fallback(config, bom_items, ws, output_path)

    shutil.copy(template_path, output_path)
    wb = openpyxl.load_workbook(output_path)
    ws = wb.active
    
    # 1. Remplissage des infos projet (B2, B3)
    safe_write(ws, 2, 2, f"Client : {config.get('client_nom', 'N/A').upper()}")
    
    type_projet = config.get('type_projet', 'Équipements')
    title = f"Équipement {type_projet}" if "équipement" not in type_projet.lower() else type_projet
    safe_write(ws, 3, 2, title)

    # 2. Gestion des items
    start_row = 4
    num_items = len(bom_items)
    
    total_row = None
    for r in range(start_row, 200):
        cell_val = ws.cell(row=r, column=6).value
        val = str(cell_val or "").upper()
        if "TOTAL" in val:
            total_row = r
            break
    
    if not total_row: total_row = 10
    
    available_rows = total_row - start_row
    
    if num_items > available_rows:
        rows_to_add = num_items - available_rows
        ws.insert_rows(total_row, rows_to_add)
        for r in range(total_row, total_row + rows_to_add):
            for c in range(1, 8):
                copy_cell_style(ws.cell(row=start_row, column=c), ws.cell(row=r, column=c))
        total_row += rows_to_add
    # Remplir les items
    total_general = 0
    for i, item in enumerate(bom_items):
        row = start_row + i
        safe_write(ws, row, 1, f"1.{i+1}")
        
        # Code : on met la marque et le modèle
        code_val = f"{item.get('marque', '')} {item.get('modele', '')}".strip()
        safe_write(ws, row, 2, code_val)
        
        # Description : la désignation ou description technique
        desc_val = item.get('designation', '') or item.get('description', '')
        safe_write(ws, row, 3, desc_val)
        
        # Unité
        safe_write(ws, row, 4, "Unit")
        
        # Quantité
        qty = item.get('quantite', 1)
        safe_write(ws, row, 5, qty)
        
        # Unit Price
        price = item.get('prix_unitaire', 0)
        safe_write(ws, row, 6, price)
        
        # Amount (Qty * Price)
        amount = qty * price
        total_general += amount
        safe_write(ws, row, 7, amount)

    # 3. Mise à jour du Total avec le format Ariary (Ar)
    # Si on a supprimé/ajouté des lignes, total_row a pu changer
    # Mais comme on a fait insert_rows avant, total_row est à jour
    safe_write(ws, total_row, 7, total_general)
    ws.cell(row=total_row, column=7).number_format = '"Ar" #,##0.00'
    
    # 4. Nettoyer les lignes inutilisées (Suppression réelle)
    if num_items < available_rows:
        # On supprime les lignes vides entre le dernier item et le total
        rows_to_delete = available_rows - num_items
        ws.delete_rows(start_row + num_items, rows_to_delete)

    # Nettoyage final du code (suppression des résidus de merge)
    wb.save(output_path)
    return output_path

def generate_bom_fallback(config, bom_items, ws, output_path):
    """Ancienne méthode de génération de zéro si le template est manquant."""
    # Configuration des colonnes
    ws.column_dimensions['A'].width = 6
    ws.column_dimensions['B'].width = 30
    ws.column_dimensions['C'].width = 60
    ws.column_dimensions['D'].width = 8
    ws.column_dimensions['E'].width = 8
    ws.column_dimensions['F'].width = 15
    ws.column_dimensions['G'].width = 15

    headers = ["#", "Code", "Description", "Unit", "Qty", "Unit Price", "Amount"]
    for col, text in enumerate(headers, 1):
        apply_magenta_style(ws.cell(row=1, column=col), bold=True, font_size=11)
        ws.cell(row=1, column=col).value = text

    # ... simplified fallback ...
    wb = ws.parent
    wb.save(output_path)
    return output_path

def generate_excel_sow(config, sow_content, bom_items=None):
    """Génère un fichier Excel SOW avec le style magenta CIMELTA."""
    template_path = os.path.join(TEMPLATES_DIR, "SOW_1.xlsx")
    filename = f"SOW_{config.get('client_nom', 'client')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    output_path = os.path.join(OUTPUT_DIR, filename)
    
    if not os.path.exists(template_path):
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "SoW"
    else:
        shutil.copy(template_path, output_path)
        wb = openpyxl.load_workbook(output_path)
        ws = wb["SoW"] if "SoW" in wb.sheetnames else wb.active
    
    # Nettoyage des fusions existantes pour le SOW car on redessine un peu les lignes
    if hasattr(ws, 'merged_cells'):
        for merge in list(ws.merged_cells.ranges):
            ws.unmerge_cells(str(merge))
    
    ws.column_dimensions['B'].width = 15
    ws.column_dimensions['C'].width = 20
    ws.column_dimensions['D'].width = 30
    ws.column_dimensions['E'].width = 50
    ws.column_dimensions['I'].width = 10

    ws["D10"] = config.get('client_nom', 'N/A')
    ws["D10"].font = Font(bold=True, color="B01B6B")
    ws["D12"] = config.get('site_intervention', 'Antananarivo')
    ws["D13"] = config.get('projet_description', '')
    
    header_row = 19
    sow_headers = ["", "Phase", "Type", "Titre", "Description", "Site", "Role", "Staff", "Durée (j)"]
    for col, text in enumerate(sow_headers, 1):
        if text:
            apply_magenta_style(ws.cell(row=header_row, column=col), bold=True)
            ws.cell(row=header_row, column=col).value = text

    taches = sow_content.get('taches', [])
    start_row = 20
    
    for i, t in enumerate(taches):
        row = start_row + i
        if i > 0:
            ws.insert_rows(row)
            
        for col in range(2, 10):
            apply_magenta_style(ws.cell(row=row, column=col), align='left' if col in [4, 5] else 'center')

        ws.cell(row=row, column=2).value = f"Phase {t.get('phase_num', 1)}"
        ws.cell(row=row, column=3).value = t.get('type', 'Implémentation')
        ws.cell(row=row, column=4).value = t.get('titre', '')
        ws.cell(row=row, column=5).value = t.get('description', '')
        ws.cell(row=row, column=6).value = config.get('site_intervention', 'Client Site')
        ws.cell(row=row, column=7).value = "Ing-1"
        ws.cell(row=row, column=8).value = 1
        ws.cell(row=row, column=9).value = t.get('duree_jours', 1)

    wb.save(output_path)
    return output_path

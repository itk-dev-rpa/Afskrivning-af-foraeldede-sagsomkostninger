from src.exceptions import BusinessError
import pywintypes
# SAP table column ids
AFTALE = 'VTREF'
BILAGSNUMMER = 'OPBEL'
AFTALE_TYPE = 'ZZAGREEMENTTYPE'
RIM_TYPE = 'ZZSBS_EFI_AGRTYPE'
AFTALE_STATUS = 'ZZAFTALESTATUS'

def delete_cost(session, fp: str, aftale: str, bilag: str, dry_run=True) -> None:
    """Pass the variables forretningspartner, aftalekonto and bilagsnummer in order to delete the dept.

    Args:
        fp: forretningspartner
        aftale: aftalekonto
        bilag: bilagsnummer
        dry_run:  when set to True, no data is changed in SAP. For production set to False.

    Raises:
        BusinessRule: When a business rule dictates that the process should stop, we raise BusinessRule exception.
        ValueError: As a measure to ensure that SAP is on the right page, or a window is present, ValueError is raised
            when those conditions are not met.
    Returns: None

    """
    session.startTransaction("fmcacov")
    session.findById('wnd[0]/usr/ctxtGPART_DYN').text = fp
    session.findById('wnd[0]').sendVKey(0)  # Press Enter

    try:
        # detect window "Forretningspartner * Entries" (pseudo table)
        session.findById('wnd[1]/usr')
        id_column = session.FindById('wnd[1]/usr/lbl[103,1]')
        if not id_column.text == "ForretnPartner":
            raise ValueError(f"Unexpected column. Expected 'ForretnPartner'. Found {id_column.text}")
        # iterate through list of PF.
        row_id = 3
        while True:
            fp_row = session.FindById(f'wnd[1]/usr/lbl[103,{row_id}]')
            if fp_row.text == fp:
                fp_row.SetFocus()
                # press 'Accept' button.
                session.FindById('wnd[1]/tbar[0]/btn[0]').press()
            row_id += 1

    except:
        # window not detected.
        pass

    try:
        postliste_table = session.FindById(
        'wnd[0]/usr/tabsDATA_DISP/tabpDATA_DISP_FC1/ssubDATA_DISP_SCA:RFMCA_COV:0202/cntlRFMCA_COV_0100_CONT5/shellcont/shell')
    except:
        print("blah!")

    # Select columns
    postliste_table.selectColumn(AFTALE)
    postliste_table.selectColumn(BILAGSNUMMER)
    # click Filter button

    postliste_table.pressToolbarButton('&MB_FILTER')

    FILTER_BOX_ID = 'wnd[1]/usr/ssub%_SUBSCREEN_FREESEL:SAPLSSEL:1105'
    # validate filter box layout
    if session.findById(f"{FILTER_BOX_ID}/txt%_%%DYN001_%_APP_%-TEXT").text != 'Aftale' or \
            session.FindById(f"{FILTER_BOX_ID}/txt%_%%DYN002_%_APP_%-TEXT").text != 'Bilagsnummer':
        raise ValueError("Filterbox unexpected layout")

    # enter Aftalenummer in filter field
    session.findById(f"{FILTER_BOX_ID}/ctxt%%DYN001-LOW").text = aftale
    # enter Bilagsnummer in filter field
    session.findById(f"{FILTER_BOX_ID}/ctxt%%DYN002-LOW").text = bilag
    session.findById('wnd[0]').sendVKey(0)  # Press Enter

    # count table rows
    row_count = postliste_table.RowCount
    if row_count == 0:
        raise BusinessError(f"Proces stoppet: Postliste for fp {fp}, Aftalenummer {aftale} er tom.")

    # check if there is anything in 'Aft.type' column
    if any([postliste_table.GetCellValue(x, AFTALE_TYPE) for x in range(row_count)]):
        raise BusinessError(f"Manuel behandling (Aft.type).")

    for x in range(row_count):
        if postliste_table.GetCellValue(x, RIM_TYPE) == 'IN' and\
                postliste_table.GetCellValue(x, AFTALE_STATUS) == '21':
            raise BusinessError("Manuel behandling: IN 21.")

    # right click and select "Kontovedligehold med filter"
    postliste_table.currentCellColumn = "VTREF"
    postliste_table.ContextMenu()
    postliste_table.SelectContextMenuItem("ACC_MAINT_FILTER")

    # click the button "Marker alle"
    session.FindById('wnd[0]/usr/subINCL_1000:SAPLFKB4:2000/btnPUSH_MA').press()

    # click the button "Aktiver poster"
    session.FindById('wnd[0]/usr/subINCL_1000:SAPLFKB4:2000/btnPUSH_PA').press()

    if dry_run:
        # do not finalize process
        return

    # click the button "Bortposter stat.poster"
    session.FindById('wnd[0]/usr/subINCL_1000:SAPLFKB4:2000/btnPUSH_CA').press()

    # click the button "Bogføring"
    session.FindById('wnd[0]/tbar[0]/btn[11]').press()

def recover_to_start_menu(session) -> None:
    """This method returns SAP to the main screen. Regardless of the current screen, attempt to return to welcome screen.
    This can be used before, after or in case of an error occurs while performing tasks in SAP.
    This is more convenient than first determining the active window of SAP.
    """
    try:
        # Already at welcome screen
        session.findById('wnd[0]/usr/cntlIMAGE_CONTAINER/shellcont/shell/shellcont[1]/shell')
        return
    except:  # TODO do fail, copy exception. import.
        session.findById('wnd[0]').sendVKey(+12)  # F12

    try:
        # Press "Ja" to abort on page Kontovedligehold
        session.findById('wnd[1]/usr/btnSPOP-OPTION1').press()
    except:
        pass

    # SAP cannot press F12 if button is greyed out
    try:
        session.findById('wnd[0]').sendVKey(12)  # F12
    except:
        pass

    try:
        session.findById('wnd[0]').sendVKey(12)  # F12
    except:
        pass

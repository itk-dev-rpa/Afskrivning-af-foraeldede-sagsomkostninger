"""Procedure for interacting with SAP using COM objects"""
import pywintypes
from afskrivining_af_foraeldede_sagsomkostninger.exceptions import BusinessError
# SAP table column ids
AFTALE = 'VTREF'
BILAGSNUMMER = 'OPBEL'
AFTALE_TYPE = 'ZZAGREEMENTTYPE'
RIM_TYPE = 'ZZSBS_EFI_AGRTYPE'
AFTALE_STATUS = 'ZZAFTALESTATUS'

def delete_cost(session, fp: str, aftale: str, bilag: str, dry_run=True) -> None:
    """Pass the variables forretningspartner, aftalekonto and bilagsnummer in order to delete the dept.

    Args:
        session: SAP GuiSession object
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

    # detect window "Forretningspartner * Entries"
    if session.findById('wnd[1]/usr', False) is not None:
        # pop-up detected
        for row_id in range(3, 5):
            fp_row = session.FindById(f'wnd[1]/usr/lbl[103,{row_id}]')
            if fp_row.text == fp:
                fp_row.SetFocus()
                # press 'Accept' button.
                session.FindById('wnd[1]/tbar[0]/btn[0]').press()
                break
        else:
            # range exhausted
            raise ValueError(f"ForretnPartner '{fp}' was not found in pop-up.")

    postliste_table = session.FindById('wnd[0]/usr/tabsDATA_DISP/tabpDATA_DISP_FC1/ssubDATA_DISP_SCA:RFMCA_COV:0202/cntlRFMCA_COV_0100_CONT5/shellcont/shell')

    # Select columns
    postliste_table.selectColumn(AFTALE)
    postliste_table.selectColumn(BILAGSNUMMER)
    # click Filter button

    postliste_table.pressToolbarButton('&MB_FILTER')

    filter_box = session.findById('wnd[1]/usr/ssub%_SUBSCREEN_FREESEL:SAPLSSEL:1105')
    # validate filter box layout
    if filter_box.findById("/txt%_%%DYN001_%_APP_%-TEXT").text != 'Aftale' or \
            filter_box.FindById("/txt%_%%DYN002_%_APP_%-TEXT").text != 'Bilagsnummer':
        raise ValueError("Filterbox unexpected layout")

    # enter Aftalenummer in filter field
    filter_box.findById("/ctxt%%DYN001-LOW").text = aftale
    # enter Bilagsnummer in filter field
    filter_box.findById("/ctxt%%DYN002-LOW").text = bilag
    session.findById('wnd[0]').sendVKey(0)  # Press Enter

    # count table rows
    row_count = postliste_table.RowCount
    if row_count == 0:
        raise BusinessError(f"Proces stoppet: Postliste for fp {fp}, Aftalenummer {aftale} er tom.")

    # check if there is anything in 'Aft.type' column
    if any(postliste_table.GetCellValue(x, AFTALE_TYPE) for x in range(row_count)):
        raise BusinessError("Manuel behandling (Aft.type).")

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
    except pywintypes.com_error:
        session.findById('wnd[0]').sendVKey(+12)  # F12

    try:
        # Press "Ja" to abort on page Kontovedligehold
        session.findById('wnd[1]/usr/btnSPOP-OPTION1').press()
    except pywintypes.com_error:
        pass

    # SAP cannot press F12 if button is greyed out
    try:
        session.findById('wnd[0]').sendVKey(12)  # F12
    except pywintypes.com_error:
        pass

    try:
        session.findById('wnd[0]').sendVKey(12)  # F12
    except pywintypes.com_error:
        pass

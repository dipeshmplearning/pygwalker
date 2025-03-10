from typing import Union, Dict, Optional
import inspect

from typing_extensions import Literal

from .pygwalker import PygWalker
from pygwalker.data_parsers.base import FieldSpec
from pygwalker.data_parsers.database_parser import Connector
from pygwalker._typing import DataFrame
from pygwalker.services.format_invoke_walk_code import get_formated_spec_params_code_from_frame
from pygwalker.utils.execute_env_check import check_convert
from pygwalker.services.global_var import GlobalVarManager


def walk(
    dataset: Union[DataFrame, Connector],
    gid: Union[int, str] = None,
    *,
    env: Literal['Jupyter', 'Streamlit', 'JupyterWidget'] = 'JupyterWidget',
    fieldSpecs: Optional[Dict[str, FieldSpec]] = None,
    hideDataSourceConfig: bool = True,
    themeKey: Literal['vega', 'g2'] = 'g2',
    dark: Literal['media', 'light', 'dark'] = 'media',
    return_html: bool = False,
    spec: str = "",
    use_preview: bool = True,
    store_chart_data: bool = False,
    use_kernel_calc: bool = False,
    **kwargs
):
    """Walk through pandas.DataFrame df with Graphic Walker

    Args:
        - dataset (pl.DataFrame | pd.DataFrame | Connector, optional): dataframe.
        - gid (Union[int, str], optional): GraphicWalker container div's id ('gwalker-{gid}')

    Kargs:
        - env: (Literal['Jupyter' | 'Streamlit'], optional): The enviroment using pygwalker. Default as 'Jupyter'
        - fieldSpecs (Dict[str, FieldSpec], optional): Specifications of some fields. They'll been automatically inferred from `df` if some fields are not specified.
        - hideDataSourceConfig (bool, optional): Hide DataSource import and export button (True) or not (False). Default to True
        - themeKey ('vega' | 'g2'): theme type.
        - dark (Literal['media' | 'light' | 'dark']): 'media': auto detect OS theme.
        - return_html (bool, optional): Directly return a html string. Defaults to False.
        - spec (str): chart config data. config id, json, remote file url
        - use_preview(bool): Whether to use preview function, Default to False.
        - store_chart_data(bool): Whether to save chart to disk, only work when spec is json file, Default to False.
    """
    if fieldSpecs is None:
        fieldSpecs = {}

    source_invoke_code = get_formated_spec_params_code_from_frame(
        inspect.stack()[1].frame
    )

    walker = PygWalker(
        gid,
        dataset,
        fieldSpecs,
        spec,
        source_invoke_code,
        hideDataSourceConfig,
        themeKey,
        dark,
        bool(GlobalVarManager.kanaries_api_key),
        use_preview,
        store_chart_data,
        isinstance(dataset, Connector) or use_kernel_calc,
        True,
        **kwargs
    )

    if return_html:
        return walker.to_html()

    if check_convert():
        env = "JupyterConvert"

    env_display_map = {
        "Streamlit": walker.display_on_streamlit,
        "JupyterWidget": walker.display_on_jupyter_use_widgets,
        "Jupyter": walker.display_on_jupyter,
        "JupyterConvert": walker.display_on_convert_html,
    }

    display_func = env_display_map.get(env, lambda: None)
    display_func()

    return walker

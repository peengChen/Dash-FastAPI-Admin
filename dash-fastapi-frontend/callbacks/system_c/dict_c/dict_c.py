import time
import uuid
from dash import ctx, dcc, no_update
from dash.dependencies import Input, Output, State, ALL
from dash.exceptions import PreventUpdate
from api.system.dict.type import DictTypeApi
from server import app
from utils.common import validate_data_not_empty
from utils.feedback_util import MessageManager
from utils.permission_util import PermissionManager


@app.callback(
    output=dict(
        dict_type_table_data=Output(
            'dict_type-list-table', 'data', allow_duplicate=True
        ),
        dict_type_table_pagination=Output(
            'dict_type-list-table', 'pagination', allow_duplicate=True
        ),
        dict_type_table_key=Output('dict_type-list-table', 'key'),
        dict_type_table_selectedrowkeys=Output(
            'dict_type-list-table', 'selectedRowKeys'
        ),
    ),
    inputs=dict(
        search_click=Input('dict_type-search', 'nClicks'),
        refresh_click=Input('dict_type-refresh', 'nClicks'),
        pagination=Input('dict_type-list-table', 'pagination'),
        operations=Input('dict_type-operations-store', 'data'),
    ),
    state=dict(
        dict_name=State('dict_type-dict_name-input', 'value'),
        dict_type=State('dict_type-dict_type-input', 'value'),
        status_select=State('dict_type-status-select', 'value'),
        create_time_range=State('dict_type-create_time-range', 'value'),
    ),
    prevent_initial_call=True,
)
def get_dict_type_table_data(
    search_click,
    refresh_click,
    pagination,
    operations,
    dict_name,
    dict_type,
    status_select,
    create_time_range,
):
    """
    获取字典类型表格数据回调（进行表格相关增删查改操作后均会触发此回调）
    """
    begin_time = None
    end_time = None
    if create_time_range:
        begin_time = create_time_range[0]
        end_time = create_time_range[1]

    query_params = dict(
        dict_name=dict_name,
        dict_type=dict_type,
        status=status_select,
        begin_time=begin_time,
        end_time=end_time,
        page_num=1,
        page_size=10,
    )
    triggered_id = ctx.triggered_id
    if triggered_id == 'dict_type-list-table':
        query_params.update(
            {
                'page_num': pagination['current'],
                'page_size': pagination['pageSize'],
            }
        )
    if search_click or refresh_click or pagination or operations:
        table_info = DictTypeApi.list_type(query_params)
        table_data = table_info['rows']
        table_pagination = dict(
            pageSize=table_info['page_size'],
            current=table_info['page_num'],
            showSizeChanger=True,
            pageSizeOptions=[10, 30, 50, 100],
            showQuickJumper=True,
            total=table_info['total'],
        )
        for item in table_data:
            if item['status'] == '0':
                item['status'] = dict(tag='正常', color='blue')
            else:
                item['status'] = dict(tag='停用', color='volcano')
            item['key'] = str(item['dict_id'])
            item['dict_type'] = {
                'content': item['dict_type'],
                'type': 'link',
            }
            item['operation'] = [
                {'content': '修改', 'type': 'link', 'icon': 'antd-edit'}
                if PermissionManager.check_perms('system:dict:edit')
                else {},
                {'content': '删除', 'type': 'link', 'icon': 'antd-delete'}
                if PermissionManager.check_perms('system:dict:remove')
                else {},
            ]

        return dict(
            dict_type_table_data=table_data,
            dict_type_table_pagination=table_pagination,
            dict_type_table_key=str(uuid.uuid4()),
            dict_type_table_selectedrowkeys=None,
        )

    raise PreventUpdate


# 重置字典类型搜索表单数据回调
app.clientside_callback(
    """
    (reset_click) => {
        if (reset_click) {
            return [null, null, null, null, {'type': 'reset'}]
        }
        return window.dash_clientside.no_update;
    }
    """,
    [
        Output('dict_type-dict_name-input', 'value'),
        Output('dict_type-dict_type-input', 'value'),
        Output('dict_type-status-select', 'value'),
        Output('dict_type-create_time-range', 'value'),
        Output('dict_type-operations-store', 'data'),
    ],
    Input('dict_type-reset', 'nClicks'),
    prevent_initial_call=True,
)


# 隐藏/显示字典类型搜索表单回调
app.clientside_callback(
    """
    (hidden_click, hidden_status) => {
        if (hidden_click) {
            return [
                !hidden_status,
                hidden_status ? '隐藏搜索' : '显示搜索'
            ]
        }
        return window.dash_clientside.no_update;
    }
    """,
    [
        Output('dict_type-search-form-container', 'hidden'),
        Output('dict_type-hidden-tooltip', 'title'),
    ],
    Input('dict_type-hidden', 'nClicks'),
    State('dict_type-search-form-container', 'hidden'),
    prevent_initial_call=True,
)


@app.callback(
    Output({'type': 'dict_type-operation-button', 'index': 'edit'}, 'disabled'),
    Input('dict_type-list-table', 'selectedRowKeys'),
    prevent_initial_call=True,
)
def change_dict_type_edit_button_status(table_rows_selected):
    """
    根据选择的表格数据行数控制编辑按钮状态回调
    """
    outputs_list = ctx.outputs_list
    if outputs_list:
        if table_rows_selected:
            if len(table_rows_selected) > 1:
                return True

            return False

        return True

    raise PreventUpdate


@app.callback(
    Output(
        {'type': 'dict_type-operation-button', 'index': 'delete'}, 'disabled'
    ),
    Input('dict_type-list-table', 'selectedRowKeys'),
    prevent_initial_call=True,
)
def change_dict_type_delete_button_status(table_rows_selected):
    """
    根据选择的表格数据行数控制删除按钮状态回调
    """
    outputs_list = ctx.outputs_list
    if outputs_list:
        if table_rows_selected:
            return False

        return True

    raise PreventUpdate


@app.callback(
    output=dict(
        modal_visible=Output(
            'dict_type-modal', 'visible', allow_duplicate=True
        ),
        modal_title=Output('dict_type-modal', 'title'),
        form_value=Output(
            {'type': 'dict_type-form-value', 'index': ALL}, 'value'
        ),
        form_label_validate_status=Output(
            {'type': 'dict_type-form-label', 'index': ALL, 'required': True},
            'validateStatus',
            allow_duplicate=True,
        ),
        form_label_validate_info=Output(
            {'type': 'dict_type-form-label', 'index': ALL, 'required': True},
            'help',
            allow_duplicate=True,
        ),
        edit_row_info=Output('dict_type-edit-id-store', 'data'),
        modal_type=Output('dict_type-operations-store-bk', 'data'),
    ),
    inputs=dict(
        operation_click=Input(
            {'type': 'dict_type-operation-button', 'index': ALL}, 'nClicks'
        ),
        button_click=Input('dict_type-list-table', 'nClicksButton'),
    ),
    state=dict(
        selected_row_keys=State('dict_type-list-table', 'selectedRowKeys'),
        clicked_content=State('dict_type-list-table', 'clickedContent'),
        recently_button_clicked_row=State(
            'dict_type-list-table', 'recentlyButtonClickedRow'
        ),
    ),
    prevent_initial_call=True,
)
def add_edit_dict_type_modal(
    operation_click,
    button_click,
    selected_row_keys,
    clicked_content,
    recently_button_clicked_row,
):
    """
    显示新增或编辑字典类型弹窗回调
    """
    trigger_id = ctx.triggered_id
    if (
        trigger_id == {'index': 'add', 'type': 'dict_type-operation-button'}
        or trigger_id == {'index': 'edit', 'type': 'dict_type-operation-button'}
        or (trigger_id == 'dict_type-list-table' and clicked_content == '修改')
    ):
        # 获取所有输出表单项对应value的index
        form_value_list = [x['id']['index'] for x in ctx.outputs_list[2]]
        # 获取所有输出表单项对应label的index
        form_label_list = [x['id']['index'] for x in ctx.outputs_list[3]]
        if trigger_id == {'index': 'add', 'type': 'dict_type-operation-button'}:
            dict_type_info = dict(
                dict_name=None,
                dict_type=None,
                status='0',
                remark=None,
            )
            return dict(
                modal_visible=True,
                modal_title='新增字典类型',
                form_value=[dict_type_info.get(k) for k in form_value_list],
                form_label_validate_status=[None] * len(form_label_list),
                form_label_validate_info=[None] * len(form_label_list),
                edit_row_info=None,
                modal_type={'type': 'add'},
            )
        elif trigger_id == {
            'index': 'edit',
            'type': 'dict_type-operation-button',
        } or (
            trigger_id == 'dict_type-list-table' and clicked_content == '修改'
        ):
            if trigger_id == {
                'index': 'edit',
                'type': 'dict_type-operation-button',
            }:
                dict_id = int(','.join(selected_row_keys))
            else:
                dict_id = int(recently_button_clicked_row['key'])
            dict_type_info_res = DictTypeApi.get_type(dict_id=dict_id)
            dict_type_info = dict_type_info_res['data']
            return dict(
                modal_visible=True,
                modal_title='编辑字典类型',
                form_value=[dict_type_info.get(k) for k in form_value_list],
                form_label_validate_status=[None] * len(form_label_list),
                form_label_validate_info=[None] * len(form_label_list),
                edit_row_info=dict_type_info if dict_type_info else None,
                modal_type={'type': 'edit'},
            )

        return dict(
            modal_visible=no_update,
            modal_title=no_update,
            form_value=[no_update] * len(form_value_list),
            form_label_validate_status=[no_update] * len(form_label_list),
            form_label_validate_info=[no_update] * len(form_label_list),
            edit_row_info=None,
            modal_type=None,
        )

    raise PreventUpdate


@app.callback(
    output=dict(
        form_label_validate_status=Output(
            {'type': 'dict_type-form-label', 'index': ALL, 'required': True},
            'validateStatus',
            allow_duplicate=True,
        ),
        form_label_validate_info=Output(
            {'type': 'dict_type-form-label', 'index': ALL, 'required': True},
            'help',
            allow_duplicate=True,
        ),
        modal_visible=Output('dict_type-modal', 'visible'),
        operations=Output(
            'dict_type-operations-store', 'data', allow_duplicate=True
        ),
    ),
    inputs=dict(confirm_trigger=Input('dict_type-modal', 'okCounts')),
    state=dict(
        modal_type=State('dict_type-operations-store-bk', 'data'),
        edit_row_info=State('dict_type-edit-id-store', 'data'),
        form_value=State(
            {'type': 'dict_type-form-value', 'index': ALL}, 'value'
        ),
        form_label=State(
            {'type': 'dict_type-form-label', 'index': ALL, 'required': True},
            'label',
        ),
    ),
    prevent_initial_call=True,
)
def dict_type_confirm(
    confirm_trigger, modal_type, edit_row_info, form_value, form_label
):
    """
    新增或编字典类型弹窗确认回调，实现新增或编辑操作
    """
    if confirm_trigger:
        # 获取所有输出表单项对应label的index
        form_label_output_list = [x['id']['index'] for x in ctx.outputs_list[0]]
        # 获取所有输入表单项对应的value及label
        form_value_state = {
            x['id']['index']: x.get('value') for x in ctx.states_list[-2]
        }
        form_label_state = {
            x['id']['index']: x.get('value') for x in ctx.states_list[-1]
        }
        if all(
            validate_data_not_empty(item)
            for item in [
                form_value_state.get(k) for k in form_label_output_list
            ]
        ):
            params_add = form_value_state
            params_edit = params_add.copy()
            params_edit['dict_id'] = (
                edit_row_info.get('dict_id') if edit_row_info else None
            )
            modal_type = modal_type.get('type')
            if modal_type == 'add':
                DictTypeApi.add_type(params_add)
            if modal_type == 'edit':
                DictTypeApi.update_type(params_edit)
            if modal_type == 'add':
                MessageManager.success(content='新增成功')

                return dict(
                    form_label_validate_status=[None]
                    * len(form_label_output_list),
                    form_label_validate_info=[None]
                    * len(form_label_output_list),
                    modal_visible=False,
                    operations={'type': 'add'},
                )
            if modal_type == 'edit':
                MessageManager.success(content='编辑成功')

                return dict(
                    form_label_validate_status=[None]
                    * len(form_label_output_list),
                    form_label_validate_info=[None]
                    * len(form_label_output_list),
                    modal_visible=False,
                    operations={'type': 'edit'},
                )

            return dict(
                form_label_validate_status=[None] * len(form_label_output_list),
                form_label_validate_info=[None] * len(form_label_output_list),
                modal_visible=no_update,
                operations=no_update,
            )

        return dict(
            form_label_validate_status=[
                None
                if validate_data_not_empty(form_value_state.get(k))
                else 'error'
                for k in form_label_output_list
            ],
            form_label_validate_info=[
                None
                if validate_data_not_empty(form_value_state.get(k))
                else f'{form_label_state.get(k)}不能为空!'
                for k in form_label_output_list
            ],
            modal_visible=no_update,
            operations=no_update,
        )

    raise PreventUpdate


@app.callback(
    [
        Output('dict_type-delete-text', 'children'),
        Output('dict_type-delete-confirm-modal', 'visible'),
        Output('dict_type-delete-ids-store', 'data'),
    ],
    [
        Input({'type': 'dict_type-operation-button', 'index': ALL}, 'nClicks'),
        Input('dict_type-list-table', 'nClicksButton'),
    ],
    [
        State('dict_type-list-table', 'selectedRowKeys'),
        State('dict_type-list-table', 'clickedContent'),
        State('dict_type-list-table', 'recentlyButtonClickedRow'),
    ],
    prevent_initial_call=True,
)
def dict_type_delete_modal(
    operation_click,
    button_click,
    selected_row_keys,
    clicked_content,
    recently_button_clicked_row,
):
    """
    显示删除字典类型二次确认弹窗回调
    """
    trigger_id = ctx.triggered_id
    if trigger_id == {
        'index': 'delete',
        'type': 'dict_type-operation-button',
    } or (trigger_id == 'dict_type-list-table' and clicked_content == '删除'):
        if trigger_id == {
            'index': 'delete',
            'type': 'dict_type-operation-button',
        }:
            dict_ids = ','.join(selected_row_keys)
        else:
            if clicked_content == '删除':
                dict_ids = recently_button_clicked_row['key']
            else:
                return no_update

        return [
            f'是否确认删除字典编号为{dict_ids}的字典类型？',
            True,
            dict_ids,
        ]

    raise PreventUpdate


@app.callback(
    Output('dict_type-operations-store', 'data', allow_duplicate=True),
    Input('dict_type-delete-confirm-modal', 'okCounts'),
    State('dict_type-delete-ids-store', 'data'),
    prevent_initial_call=True,
)
def dict_type_delete_confirm(delete_confirm, dict_ids_data):
    """
    删除字典类型弹窗确认回调，实现删除操作
    """
    if delete_confirm:
        params = dict_ids_data
        DictTypeApi.del_type(params)
        MessageManager.success(content='删除成功')

        return {'type': 'delete'}

    raise PreventUpdate


@app.callback(
    output=dict(
        dict_data_modal_visible=Output(
            'dict_type_to_dict_data-modal', 'visible'
        ),
        dict_data_modal_title=Output('dict_type_to_dict_data-modal', 'title'),
        dict_data_select_options=Output(
            'dict_data-dict_type-select', 'options'
        ),
        dict_data_select_value=Output(
            'dict_data-dict_type-select', 'value', allow_duplicate=True
        ),
        dict_data_search_nclick=Output('dict_data-search', 'nClicks'),
    ),
    inputs=dict(button_click=Input('dict_type-list-table', 'nClicksButton')),
    state=dict(
        clicked_content=State('dict_type-list-table', 'clickedContent'),
        recently_button_clicked_row=State(
            'dict_type-list-table', 'recentlyButtonClickedRow'
        ),
        dict_data_search_nclick=State('dict_data-search', 'nClicks'),
    ),
    prevent_initial_call=True,
)
def dict_type_to_dict_data_modal(
    button_click,
    clicked_content,
    recently_button_clicked_row,
    dict_data_search_nclick,
):
    """
    显示字典类型对应数据表格弹窗回调
    """

    if button_click and clicked_content == recently_button_clicked_row.get(
        'dict_type'
    ).get('content'):
        all_dict_type_info = DictTypeApi.optionselect()
        all_dict_type = all_dict_type_info.get('data')
        dict_data_options = [
            dict(label=item.get('dict_name'), value=item.get('dict_type'))
            for item in all_dict_type
        ]

        return dict(
            dict_data_modal_visible=True,
            dict_data_modal_title='字典数据',
            dict_data_select_options=dict_data_options,
            dict_data_select_value=recently_button_clicked_row.get(
                'dict_type'
            ).get('content'),
            dict_data_search_nclick=dict_data_search_nclick + 1
            if dict_data_search_nclick
            else 1,
        )

    raise PreventUpdate


@app.callback(
    [
        Output('dict_type-export-container', 'data', allow_duplicate=True),
        Output('dict_type-export-complete-judge-container', 'data'),
    ],
    Input('dict_type-export', 'nClicks'),
    prevent_initial_call=True,
)
def export_dict_type_list(export_click):
    """
    导出字典类型信息回调
    """
    if export_click:
        export_dict_type_res = DictTypeApi.export_type({})
        export_dict_type = export_dict_type_res.content
        MessageManager.success(content='导出成功')

        return [
            dcc.send_bytes(
                export_dict_type,
                f'字典类型信息_{time.strftime("%Y%m%d%H%M%S", time.localtime())}.xlsx',
            ),
            {'timestamp': time.time()},
        ]

    raise PreventUpdate


@app.callback(
    Output('dict_type-export-container', 'data', allow_duplicate=True),
    Input('dict_type-export-complete-judge-container', 'data'),
    prevent_initial_call=True,
)
def reset_dict_type_export_status(data):
    """
    导出完成后重置下载组件数据回调，防止重复下载文件
    """
    time.sleep(0.5)
    if data:
        return None

    raise PreventUpdate


@app.callback(
    Input('dict_type-refresh-cache', 'nClicks'),
    prevent_initial_call=True,
)
def refresh_dict_cache(refresh_click):
    """
    刷新缓存回调
    """
    if refresh_click:
        DictTypeApi.refresh_cache()
        MessageManager.success(content='刷新成功')

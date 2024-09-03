import dash
import time
import uuid
import json
from dash.dependencies import Input, Output, State, ALL
from dash.exceptions import PreventUpdate
import feffery_utils_components as fuc

from server import app
from utils.common import validate_data_not_empty
from api.system.notice import NoticeApi
from api.system.dict.data import DictDataApi
from utils.permission_util import PermissionManager


@app.callback(
    output=dict(
        notice_table_data=Output(
            'notice-list-table', 'data', allow_duplicate=True
        ),
        notice_table_pagination=Output(
            'notice-list-table', 'pagination', allow_duplicate=True
        ),
        notice_table_key=Output('notice-list-table', 'key'),
        notice_table_selectedrowkeys=Output(
            'notice-list-table', 'selectedRowKeys'
        ),
        api_check_token_trigger=Output(
            'api-check-token', 'data', allow_duplicate=True
        ),
    ),
    inputs=dict(
        search_click=Input('notice-search', 'nClicks'),
        refresh_click=Input('notice-refresh', 'nClicks'),
        pagination=Input('notice-list-table', 'pagination'),
        operations=Input('notice-operations-store', 'data'),
    ),
    state=dict(
        notice_title=State('notice-notice_title-input', 'value'),
        update_by=State('notice-update_by-input', 'value'),
        notice_type=State('notice-notice_type-select', 'value'),
        create_time_range=State('notice-create_time-range', 'value'),
    ),
    prevent_initial_call=True,
)
def get_notice_table_data(
    search_click,
    refresh_click,
    pagination,
    operations,
    notice_title,
    update_by,
    notice_type,
    create_time_range,
):
    """
    获取通知公告表格数据回调（进行表格相关增删查改操作后均会触发此回调）
    """
    begin_time = None
    end_time = None
    if create_time_range:
        begin_time = create_time_range[0]
        end_time = create_time_range[1]

    query_params = dict(
        notice_title=notice_title,
        update_by=update_by,
        notice_type=notice_type,
        begin_time=begin_time,
        end_time=end_time,
        page_num=1,
        page_size=10,
    )
    triggered_id = dash.ctx.triggered_id
    if triggered_id == 'notice-list-table':
        query_params.update(
            {
                'page_num': pagination['current'],
                'page_size': pagination['pageSize'],
            }
        )
    if search_click or refresh_click or pagination or operations:
        option_table = []
        info = DictDataApi.get_dicts(dict_type='sys_notice_type')
        if info.get('code') == 200:
            data = info.get('data')
            option_table = [
                dict(
                    label=item.get('dict_label'),
                    value=item.get('dict_value'),
                    css_class=item.get('css_class'),
                )
                for item in data
            ]
        option_dict = {item.get('value'): item for item in option_table}

        table_info = NoticeApi.list_notice(query_params)
        if table_info['code'] == 200:
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
                    item['status'] = dict(tag='关闭', color='volcano')
                item['notice_type'] = dict(
                    tag=option_dict.get(str(item.get('notice_type'))).get(
                        'label'
                    ),
                    color='blue',
                )
                item['key'] = str(item['notice_id'])
                item['operation'] = [
                    {'content': '修改', 'type': 'link', 'icon': 'antd-edit'}
                    if PermissionManager.check_perms('system:notice:edit')
                    else {},
                    {'content': '删除', 'type': 'link', 'icon': 'antd-delete'}
                    if PermissionManager.check_perms('system:notice:remove')
                    else {},
                ]

            return dict(
                notice_table_data=table_data,
                notice_table_pagination=table_pagination,
                notice_table_key=str(uuid.uuid4()),
                notice_table_selectedrowkeys=None,
                api_check_token_trigger={'timestamp': time.time()},
            )

        return dict(
            notice_table_data=dash.no_update,
            notice_table_pagination=dash.no_update,
            notice_table_key=dash.no_update,
            notice_table_selectedrowkeys=dash.no_update,
            api_check_token_trigger={'timestamp': time.time()},
        )

    raise PreventUpdate


# 重置通知公告搜索表单数据回调
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
        Output('notice-notice_title-input', 'value'),
        Output('notice-update_by-input', 'value'),
        Output('notice-notice_type-select', 'value'),
        Output('notice-create_time-range', 'value'),
        Output('notice-operations-store', 'data'),
    ],
    Input('notice-reset', 'nClicks'),
    prevent_initial_call=True,
)


# 隐藏/显示通知公告搜索表单回调
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
        Output('notice-search-form-container', 'hidden'),
        Output('notice-hidden-tooltip', 'title'),
    ],
    Input('notice-hidden', 'nClicks'),
    State('notice-search-form-container', 'hidden'),
    prevent_initial_call=True,
)


@app.callback(
    Output({'type': 'notice-operation-button', 'index': 'edit'}, 'disabled'),
    Input('notice-list-table', 'selectedRowKeys'),
    prevent_initial_call=True,
)
def change_notice_edit_button_status(table_rows_selected):
    """
    根据选择的表格数据行数控制编辑按钮状态回调
    """
    outputs_list = dash.ctx.outputs_list
    if outputs_list:
        if table_rows_selected:
            if len(table_rows_selected) > 1:
                return True

            return False

        return True

    raise PreventUpdate


@app.callback(
    Output({'type': 'notice-operation-button', 'index': 'delete'}, 'disabled'),
    Input('notice-list-table', 'selectedRowKeys'),
    prevent_initial_call=True,
)
def change_notice_delete_button_status(table_rows_selected):
    """
    根据选择的表格数据行数控制删除按钮状态回调
    """
    outputs_list = dash.ctx.outputs_list
    if outputs_list:
        if table_rows_selected:
            return False

        return True

    raise PreventUpdate


@app.callback(
    output=dict(
        modal=dict(
            visible=Output('notice-modal', 'visible', allow_duplicate=True),
            title=Output('notice-modal', 'title'),
        ),
        form_value=dict(
            notice_title=Output('notice-notice_title', 'value'),
            notice_type=Output('notice-notice_type', 'value'),
            status=Output('notice-status', 'value'),
            notice_content=Output('notice-content', 'htmlValue'),
            editor_key=Output('notice-content', 'key'),
        ),
        form_validate=[
            Output(
                'notice-notice_title-form-item',
                'validateStatus',
                allow_duplicate=True,
            ),
            Output(
                'notice-notice_type-form-item',
                'validateStatus',
                allow_duplicate=True,
            ),
            Output(
                'notice-notice_title-form-item', 'help', allow_duplicate=True
            ),
            Output(
                'notice-notice_type-form-item', 'help', allow_duplicate=True
            ),
        ],
        other=dict(
            api_check_token_trigger=Output(
                'api-check-token', 'data', allow_duplicate=True
            ),
            edit_row_info=Output('notice-edit-id-store', 'data'),
            modal_type=Output('notice-operations-store-bk', 'data'),
        ),
    ),
    inputs=dict(
        operation_click=Input(
            {'type': 'notice-operation-button', 'index': ALL}, 'nClicks'
        ),
        button_click=Input('notice-list-table', 'nClicksButton'),
    ),
    state=dict(
        selected_row_keys=State('notice-list-table', 'selectedRowKeys'),
        clicked_content=State('notice-list-table', 'clickedContent'),
        recently_button_clicked_row=State(
            'notice-list-table', 'recentlyButtonClickedRow'
        ),
    ),
    prevent_initial_call=True,
)
def add_edit_notice_modal(
    operation_click,
    button_click,
    selected_row_keys,
    clicked_content,
    recently_button_clicked_row,
):
    """
    显示新增或编辑通知公告弹窗回调
    """
    trigger_id = dash.ctx.triggered_id
    if (
        trigger_id == {'index': 'add', 'type': 'notice-operation-button'}
        or trigger_id == {'index': 'edit', 'type': 'notice-operation-button'}
        or (trigger_id == 'notice-list-table' and clicked_content == '修改')
    ):
        if trigger_id == {'index': 'add', 'type': 'notice-operation-button'}:
            return dict(
                modal=dict(visible=True, title='新增通知公告'),
                form_value=dict(
                    notice_title=None,
                    notice_type=None,
                    status='0',
                    notice_content=None,
                    editor_key=str(uuid.uuid4()),
                ),
                form_validate=[None] * 4,
                other=dict(
                    api_check_token_trigger=dash.no_update,
                    edit_row_info=None,
                    modal_type={'type': 'add'},
                ),
            )
        elif trigger_id == {
            'index': 'edit',
            'type': 'notice-operation-button',
        } or (trigger_id == 'notice-list-table' and clicked_content == '修改'):
            if trigger_id == {
                'index': 'edit',
                'type': 'notice-operation-button',
            }:
                notice_id = int(','.join(selected_row_keys))
            else:
                notice_id = int(recently_button_clicked_row['key'])
            notice_info_res = NoticeApi.get_notice(notice_id=notice_id)
            if notice_info_res['code'] == 200:
                notice_info = notice_info_res['data']
                notice_content = notice_info.get('notice_content')

                return dict(
                    modal=dict(visible=True, title='编辑通知公告'),
                    form_value=dict(
                        notice_title=notice_info.get('notice_title'),
                        notice_type=notice_info.get('notice_type'),
                        status=notice_info.get('status'),
                        notice_content=notice_content,
                        editor_key=str(uuid.uuid4()),
                    ),
                    form_validate=[None] * 4,
                    other=dict(
                        api_check_token_trigger={'timestamp': time.time()},
                        edit_row_info=notice_info if notice_info else None,
                        modal_type={'type': 'edit'},
                    ),
                )

        return dict(
            modal=dict(visible=dash.no_update, title=dash.no_update),
            form_value=dict(
                notice_title=dash.no_update,
                notice_type=dash.no_update,
                status=dash.no_update,
                notice_content=dash.no_update,
                editor_key=dash.no_update,
            ),
            form_validate=[dash.no_update] * 4,
            other=dict(
                api_check_token_trigger={'timestamp': time.time()},
                edit_row_info=None,
                modal_type=None,
            ),
        )

    raise PreventUpdate


@app.callback(
    output=dict(
        notice_title_form_status=Output(
            'notice-notice_title-form-item',
            'validateStatus',
            allow_duplicate=True,
        ),
        notice_type_form_status=Output(
            'notice-notice_type-form-item',
            'validateStatus',
            allow_duplicate=True,
        ),
        notice_title_form_help=Output(
            'notice-notice_title-form-item', 'help', allow_duplicate=True
        ),
        notice_type_form_help=Output(
            'notice-notice_type-form-item', 'help', allow_duplicate=True
        ),
        modal_visible=Output('notice-modal', 'visible'),
        operations=Output(
            'notice-operations-store', 'data', allow_duplicate=True
        ),
        api_check_token_trigger=Output(
            'api-check-token', 'data', allow_duplicate=True
        ),
        global_message_container=Output(
            'global-message-container', 'children', allow_duplicate=True
        ),
    ),
    inputs=dict(confirm_trigger=Input('notice-modal', 'okCounts')),
    state=dict(
        modal_type=State('notice-operations-store-bk', 'data'),
        edit_row_info=State('notice-edit-id-store', 'data'),
        notice_title=State('notice-notice_title', 'value'),
        notice_type=State('notice-notice_type', 'value'),
        status=State('notice-status', 'value'),
        notice_content=State('notice-content', 'htmlValue'),
    ),
    prevent_initial_call=True,
)
def notice_confirm(
    confirm_trigger,
    modal_type,
    edit_row_info,
    notice_title,
    notice_type,
    status,
    notice_content,
):
    """
    新增或编辑通知公告弹窗确认回调，实现新增或编辑操作
    """
    if confirm_trigger:
        if all(
            validate_data_not_empty(item)
            for item in [notice_title, notice_type]
        ):
            params_add = dict(
                notice_title=notice_title,
                notice_type=notice_type,
                status=status,
                notice_content=notice_content,
            )
            params_edit = dict(
                notice_id=edit_row_info.get('notice_id')
                if edit_row_info
                else None,
                notice_title=notice_title,
                notice_type=notice_type,
                status=status,
                notice_content=notice_content,
            )
            api_res = {}
            modal_type = modal_type.get('type')
            if modal_type == 'add':
                api_res = NoticeApi.add_notice(params_add)
            if modal_type == 'edit':
                api_res = NoticeApi.update_notice(params_edit)
            if api_res.get('code') == 200:
                if modal_type == 'add':
                    return dict(
                        notice_title_form_status=None,
                        notice_type_form_status=None,
                        notice_title_form_help=None,
                        notice_type_form_help=None,
                        modal_visible=False,
                        operations={'type': 'add'},
                        api_check_token_trigger={'timestamp': time.time()},
                        global_message_container=fuc.FefferyFancyMessage(
                            '新增成功', type='success'
                        ),
                    )
                if modal_type == 'edit':
                    return dict(
                        notice_title_form_status=None,
                        notice_type_form_status=None,
                        notice_title_form_help=None,
                        notice_type_form_help=None,
                        modal_visible=False,
                        operations={'type': 'edit'},
                        api_check_token_trigger={'timestamp': time.time()},
                        global_message_container=fuc.FefferyFancyMessage(
                            '编辑成功', type='success'
                        ),
                    )

            return dict(
                notice_title_form_status=None,
                notice_type_form_status=None,
                notice_title_form_help=None,
                notice_type_form_help=None,
                modal_visible=dash.no_update,
                operations=dash.no_update,
                api_check_token_trigger={'timestamp': time.time()},
                global_message_container=fuc.FefferyFancyMessage(
                    '处理失败', type='error'
                ),
            )

        return dict(
            notice_title_form_status=None
            if validate_data_not_empty(notice_title)
            else 'error',
            notice_type_form_status=None
            if validate_data_not_empty(notice_type)
            else 'error',
            notice_title_form_help=None
            if validate_data_not_empty(notice_title)
            else '请输入公告标题！',
            notice_type_form_help=None
            if validate_data_not_empty(notice_type)
            else '请输入公告类型！',
            modal_visible=dash.no_update,
            operations=dash.no_update,
            api_check_token_trigger=dash.no_update,
            global_message_container=fuc.FefferyFancyMessage(
                '处理失败', type='error'
            ),
        )

    raise PreventUpdate


@app.callback(
    [
        Output('notice-delete-text', 'children'),
        Output('notice-delete-confirm-modal', 'visible'),
        Output('notice-delete-ids-store', 'data'),
    ],
    [
        Input({'type': 'notice-operation-button', 'index': ALL}, 'nClicks'),
        Input('notice-list-table', 'nClicksButton'),
    ],
    [
        State('notice-list-table', 'selectedRowKeys'),
        State('notice-list-table', 'clickedContent'),
        State('notice-list-table', 'recentlyButtonClickedRow'),
    ],
    prevent_initial_call=True,
)
def notice_delete_modal(
    operation_click,
    button_click,
    selected_row_keys,
    clicked_content,
    recently_button_clicked_row,
):
    """
    显示删除通知公告二次确认弹窗回调
    """
    trigger_id = dash.ctx.triggered_id
    if trigger_id == {'index': 'delete', 'type': 'notice-operation-button'} or (
        trigger_id == 'notice-list-table' and clicked_content == '删除'
    ):
        trigger_id = dash.ctx.triggered_id

        if trigger_id == {'index': 'delete', 'type': 'notice-operation-button'}:
            notice_ids = ','.join(selected_row_keys)
        else:
            if clicked_content == '删除':
                notice_ids = recently_button_clicked_row['key']
            else:
                return dash.no_update

        return [f'是否确认删除序号为{notice_ids}的通知公告？', True, notice_ids]

    raise PreventUpdate


@app.callback(
    [
        Output('notice-operations-store', 'data', allow_duplicate=True),
        Output('api-check-token', 'data', allow_duplicate=True),
        Output('global-message-container', 'children', allow_duplicate=True),
    ],
    Input('notice-delete-confirm-modal', 'okCounts'),
    State('notice-delete-ids-store', 'data'),
    prevent_initial_call=True,
)
def notice_delete_confirm(delete_confirm, notice_ids_data):
    """
    删除岗通知公告弹窗确认回调，实现删除操作
    """
    if delete_confirm:
        params = notice_ids_data
        delete_button_info = NoticeApi.del_notice(params)
        if delete_button_info['code'] == 200:
            return [
                {'type': 'delete'},
                {'timestamp': time.time()},
                fuc.FefferyFancyMessage('删除成功', type='success'),
            ]

        return [
            dash.no_update,
            {'timestamp': time.time()},
            fuc.FefferyFancyMessage('删除失败', type='error'),
        ]

    raise PreventUpdate

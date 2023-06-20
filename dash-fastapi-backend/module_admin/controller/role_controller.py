from fastapi import APIRouter, Request
from fastapi import Depends, Header
from config.get_db import get_db
from module_admin.service.login_service import get_current_user
from module_admin.service.role_service import *
from module_admin.entity.vo.role_schema import *
from module_admin.utils.response_tool import *
from module_admin.utils.log_tool import *


roleController = APIRouter(dependencies=[Depends(get_current_user)])


@roleController.post("/role/forSelectOption", response_model=RoleSelectOptionResponseModel)
async def get_system_role_select(query_db: Session = Depends(get_db)):
    try:
        role_query_result = get_role_select_option_services(query_db)
        logger.info('获取成功')
        return response_200(data=role_query_result, message="获取成功")
    except Exception as e:
        logger.exception(e)
        return response_500(data="", message="接口异常")
    
    
@roleController.post("/role/get", response_model=RolePageObjectResponse)
async def get_system_role_list(role_query: RolePageObject, query_db: Session = Depends(get_db)):
    try:
        role_query_result = get_role_list_services(query_db, role_query)
        logger.info('获取成功')
        return response_200(data=role_query_result, message="获取成功")
    except Exception as e:
        logger.exception(e)
        return response_500(data="", message="接口异常")
    
    
@roleController.post("/role/add", response_model=CrudRoleResponse)
async def add_system_role(request: Request, add_role: AddRoleModel, token: Optional[str] = Header(...), query_db: Session = Depends(get_db)):
    try:
        current_user = await get_current_user(request, token, query_db)
        add_role.create_by = current_user.user.user_name
        add_role.update_by = current_user.user.user_name
        add_role_result = add_role_services(query_db, add_role)
        logger.info(add_role_result.message)
        if add_role_result.is_success:
            return response_200(data=add_role_result, message=add_role_result.message)
        else:
            return response_400(data="", message=add_role_result.message)
    except Exception as e:
        logger.exception(e)
        return response_500(data="", message="接口异常")
    
    
@roleController.patch("/role/edit", response_model=CrudRoleResponse)
async def edit_system_role(request: Request, edit_role: AddRoleModel, token: Optional[str] = Header(...), query_db: Session = Depends(get_db)):
    try:
        current_user = await get_current_user(request, token, query_db)
        edit_role.update_by = current_user.user.user_name
        edit_role.update_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        edit_role_result = edit_role_services(query_db, edit_role)
        if edit_role_result.is_success:
            logger.info(edit_role_result.message)
            return response_200(data=edit_role_result, message=edit_role_result.message)
        else:
            logger.warning(edit_role_result.message)
            return response_400(data="", message=edit_role_result.message)
    except Exception as e:
        logger.exception(e)
        return response_500(data="", message="接口异常")
    
    
@roleController.post("/role/delete", response_model=CrudRoleResponse)
async def delete_system_role(request: Request, delete_role: DeleteRoleModel, token: Optional[str] = Header(...), query_db: Session = Depends(get_db)):
    try:
        current_user = await get_current_user(request, token, query_db)
        delete_role.update_by = current_user.user.user_name
        delete_role.update_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        delete_role_result = delete_role_services(query_db, delete_role)
        if delete_role_result.is_success:
            logger.info(delete_role_result.message)
            return response_200(data=delete_role_result, message=delete_role_result.message)
        else:
            logger.warning(delete_role_result.message)
            return response_400(data="", message=delete_role_result.message)
    except Exception as e:
        logger.exception(e)
        return response_500(data="", message="接口异常")
    
    
@roleController.get("/role/{role_id}", response_model=RoleDetailModel)
async def query_detail_system_role(role_id: int, query_db: Session = Depends(get_db)):
    try:
        delete_role_result = detail_role_services(query_db, role_id)
        logger.info(f'获取role_id为{role_id}的信息成功')
        return response_200(data=delete_role_result, message='获取成功')
    except Exception as e:
        logger.exception(e)
        return response_500(data="", message="接口异常")
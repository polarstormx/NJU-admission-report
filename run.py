from dtable import NjuTableAuth
import base64
from dotenv import load_dotenv
import logging
import os
ROOT_URL = 'https://table.nju.edu.cn'
TABLE_TOKEN = 'acb58836-10ae-4ec0-a2bf-8cce3245a373'



auth = NjuTableAuth(TABLE_TOKEN)


if __name__ == "__main__":
    load_dotenv(verbose=True)
    logging.basicConfig(
        level=logging.INFO, format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
    log = logging.getLogger()

    username = os.getenv('NJU_USERNAME')
    password = os.getenv('NJU_PASSWORD')
    name = os.getenv('NAME')
    skm_pic = os.getenv('SKM_PIC')
    xcm_pic = os.getenv('XCM_PIC')

    if username == None or password == None:
        log.error('账户或密码信息为空！请检查是否正确地设置了 SECRET 项（GitHub Action）。')
        os._exit(1)

    if skm_pic == None or xcm_pic == None:
        log.error('苏康码或行程码截图为空！请检查是否正确地设置了 SECRET 项（GitHub Action）。')
        os._exit(1)
    try:
        skm_pic = base64.b64decode(skm_pic)
        xcm_pic = base64.b64decode(xcm_pic)
    except Exception as e:
        log.error('苏康码、行程码解析错误！请确保使用了base64格式在 SECRET 项中存储')
        log.error(e)
        os._exit(1)

    ok = auth.login(username, password)
    if not ok:
        log.error('登陆失败')
        os._exit(1)
    log.info('登录成功！')

    # upload skm_pic
    try:
        upload_info = auth.getUploadLinkViaFormToken(TABLE_TOKEN)
        assert upload_info is not None and upload_info != "", f'getUploadLink Error,{upload_info}'
        upload_info = dict(eval(upload_info))
        skm_name = auth.uploadPic(upload_info['upload_link'], upload_info['parent_path'],
                                  upload_info['img_relative_path'], skm_pic)
        # upload xcm_pic
        upload_info = auth.getUploadLinkViaFormToken(TABLE_TOKEN)
        assert upload_info is not None and upload_info != "", f'getUploadLink Error,{upload_info}'
        upload_info = dict(eval(upload_info))
        xcm_name = auth.uploadPic(upload_info['upload_link'], upload_info['parent_path'],
                                  upload_info['img_relative_path'], xcm_pic)

        # TODO：变更项
        submit_data = {
            '人员': name,
            '学号': username,
            '苏康码截图': [f'{ROOT_URL}/dtable/forms/{TABLE_TOKEN}/asset/{skm_name}'],
            '行程码截图': [f'{ROOT_URL}/dtable/forms/{TABLE_TOKEN}/asset/{xcm_name}']
        }
        ok = auth.submit_form(TABLE_TOKEN, submit_data)
        if not ok:
            log.error("申报失败，请手动申报")
            os._exit(1)
        else:
            log.info("申报成功！")
    except Exception as e:
        log.error("申报失败，可能是超出申报时间")
        log.error(e)
        os._exit(1)

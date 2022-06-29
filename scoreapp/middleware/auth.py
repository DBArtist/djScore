from django.utils.deprecation import MiddlewareMixin
from django.shortcuts import HttpResponse,redirect


class AuthMiddleware(MiddlewareMixin):
    """ 中间件1 """
    def process_request(self,request):
        # 0.排除不需要登录就能访问的页面
        # request.path_info
        if request.path_info in ["/login/","/image/code/"]:
            return

        # 1.读取当前访问用户的session信息。
        info_dict = request.session.get("info")
        if info_dict:
            return

        # 2.没有登录信息
        return redirect("/login")

    # def process_response(self,request,response):
    #     print("M1.process_response")
    #     return response




# class M1(MiddlewareMixin):
#     """ 中间件1 """
#     def process_request(self,request):
#         print("M1.process_request")
#
#     def process_response(self,request,response):
#         print("M1.process_response")
#         return response
#
#
# class M2(MiddlewareMixin):
#     """ 中间件2 """
#
#     def process_request(self, request):
#         print("M2.process_request")
#
#     def process_response(self, request, response):
#         print("M2.process_response")
#         return response

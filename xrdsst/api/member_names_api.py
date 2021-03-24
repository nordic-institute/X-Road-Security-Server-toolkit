# coding: utf-8

"""
    X-Road Security Server Admin API

    X-Road Security Server Admin API. Note that the error metadata responses described in some endpoints are subjects to change and may be updated in upcoming versions.  # noqa: E501

    OpenAPI spec version: 1.0.31
    Contact: info@niis.org
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""

from __future__ import absolute_import

import re  # noqa: F401

# python 2 and python 3 compatibility library
import six

from xrdsst.api_client.api_client import ApiClient


class MemberNamesApi(object):
    """NOTE: This class is auto generated by the swagger code generator program.

    Do not edit the class manually.
    Ref: https://github.com/swagger-api/swagger-codegen
    """

    def __init__(self, api_client=None):
        if api_client is None:
            api_client = ApiClient()
        self.api_client = api_client

    def find_member_name(self, member_class, member_code, **kwargs):  # noqa: E501
        """find member name by member class and member code  # noqa: E501

        <h3>Administrator looks up member's name.</h3>  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.find_member_name(member_class, member_code, async_req=True)
        >>> result = thread.get()

        :param async_req bool
        :param str member_class: class of the member (required)
        :param str member_code: code of the member (required)
        :return: MemberName
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('async_req'):
            return self.find_member_name_with_http_info(member_class, member_code, **kwargs)  # noqa: E501
        else:
            (data) = self.find_member_name_with_http_info(member_class, member_code, **kwargs)  # noqa: E501
            return data

    def find_member_name_with_http_info(self, member_class, member_code, **kwargs):  # noqa: E501
        """find member name by member class and member code  # noqa: E501

        <h3>Administrator looks up member's name.</h3>  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.find_member_name_with_http_info(member_class, member_code, async_req=True)
        >>> result = thread.get()

        :param async_req bool
        :param str member_class: class of the member (required)
        :param str member_code: code of the member (required)
        :return: MemberName
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = ['member_class', 'member_code']  # noqa: E501
        all_params.append('async_req')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method find_member_name" % key
                )
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'member_class' is set
        if ('member_class' not in params or
                params['member_class'] is None):
            raise ValueError("Missing the required parameter `member_class` when calling `find_member_name`")  # noqa: E501
        # verify the required parameter 'member_code' is set
        if ('member_code' not in params or
                params['member_code'] is None):
            raise ValueError("Missing the required parameter `member_code` when calling `find_member_name`")  # noqa: E501

        collection_formats = {}

        path_params = {}

        query_params = []
        if 'member_class' in params:
            query_params.append(('member_class', params['member_class']))  # noqa: E501
        if 'member_code' in params:
            query_params.append(('member_code', params['member_code']))  # noqa: E501

        header_params = {}

        form_params = []
        local_var_files = {}

        body_params = None
        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept(
            ['application/json'])  # noqa: E501

        # Authentication setting
        auth_settings = ['ApiKeyAuth']  # noqa: E501

        return self.api_client.call_api(
            '/member-names', 'GET',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=local_var_files,
            response_type='MemberName',  # noqa: E501
            auth_settings=auth_settings,
            async_req=params.get('async_req'),
            _return_http_data_only=params.get('_return_http_data_only'),
            _preload_content=params.get('_preload_content', True),
            _request_timeout=params.get('_request_timeout'),
            collection_formats=collection_formats)

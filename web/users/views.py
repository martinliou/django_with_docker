import json
from users.models import Users, session
from users.serializers import UsersSerializer
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.views import APIView
from django.http import JsonResponse
from django.core.exceptions import ObjectDoesNotExist
from sqlalchemy.exc import IntegrityError
from django.contrib.auth.hashers import make_password, check_password
from app.jwt import get_tokens_for_user
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from app.wsclient import send_signin_fail

class UserAPIView(APIView):

    @swagger_auto_schema(methods=['get'], operation_description="Get user list", manual_parameters=[
        openapi.Parameter('order_by', openapi.IN_QUERY,
                          "one of following items: acct, fullname, created_at or updated_at", type=openapi.TYPE_STRING),
        openapi.Parameter('sort', openapi.IN_QUERY,
                          "asc or desc", type=openapi.TYPE_STRING),
        openapi.Parameter('limit', openapi.IN_QUERY,
                          "Used for pagination, number of request for objects", type=openapi.TYPE_STRING),
        openapi.Parameter('offset', openapi.IN_QUERY,
                          "Used for pagination, number of skip for objects", type=openapi.TYPE_STRING),
    ], responses={
        200: openapi.Response('Response', UsersSerializer),
    }, tags=['User list'])
    @api_view(['GET'])
    @permission_classes([IsAuthenticated])
    def list(request):
        '''This method is used to get user list'''
        params = request.GET
        users = session.query(Users)
        order_fields = ['acct', 'fullname', 'created_at', 'updated_at']
        sort_fields = ['asc', 'desc']

        # Order by and sort should be checked before limit and offset, or result in SQL query error
        if params.get('order_by', str()) in order_fields and \
                params.get('sort', str()) in sort_fields:
            users = users.order_by(
                eval('Users.{}.{}()'.format(params['order_by'], params['sort'])))

        if params.get('limit', str()).isdigit():
            users = users.limit(params['limit'])

        if params.get('offset', str()).isdigit():
            users = users.offset(params['offset'])

        serializer = UsersSerializer(users, many=True)
        return JsonResponse({
            'status': 0,
            'data': serializer.data
        },
            status=status.HTTP_200_OK)

    @swagger_auto_schema(methods=['get'], operation_description="Searching specified user within given full name", manual_parameters=[
        openapi.Parameter('fullname', openapi.IN_QUERY,
                          "User fullname", type=openapi.TYPE_STRING),
    ], responses={
        200: openapi.Response('Response', UsersSerializer),
    }, tags=['User search'])
    @api_view(['GET'])
    @permission_classes([IsAuthenticated])
    def search(request):
        '''This method is used for searching specified user within given full name'''
        try:
            params = request.GET
            users = session.query(Users).filter_by(
                fullname=params.get('fullname')).all()

            if users:
                serializer = UsersSerializer(users[0], many=False)
                return JsonResponse({
                    'status': 0,
                    'data': serializer.data
                },
                    status=status.HTTP_200_OK
                )
            else:
                raise ObjectDoesNotExist

        except ObjectDoesNotExist as e:
            return JsonResponse({
                'status': -1,
                'message': 'Cannot find target user'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return JsonResponse({
                'status': -1,
                'message': 'Search error'
            },
                status=status.HTTP_422_UNPROCESSABLE_ENTITY)

    @swagger_auto_schema(methods=['get'], operation_description="Get specified user info within given account ID", manual_parameters=[
        openapi.Parameter('acct', openapi.IN_PATH,
                          "User account", type=openapi.TYPE_STRING),
    ], responses={
        200: openapi.Response('Response', UsersSerializer),
    }, tags=['User details'])
    @api_view(['GET'])
    @permission_classes([IsAuthenticated])
    def details(request, acct):
        '''This method is used for getting specified user info within given account ID'''
        try:
            user = session.query(Users).get(acct)

            if user:
                serializer = UsersSerializer(user, many=False)
                return JsonResponse({
                    'status': 0,
                    'data': serializer.data
                },
                    status=status.HTTP_200_OK
                )
            else:
                raise ObjectDoesNotExist

        except ObjectDoesNotExist as e:
            return JsonResponse({
                'status': -1,
                'message': 'Cannot find target user'
            }, status=status.HTTP_404_NOT_FOUND)
        except:
            return JsonResponse({
                'status': -1,
                'message': 'Details lookup error'
            },
                status=status.HTTP_422_UNPROCESSABLE_ENTITY)

    @swagger_auto_schema(methods=['post'], operation_description="Signing up within account ID, fullname and password", request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'acct': openapi.Schema(type=openapi.TYPE_STRING, description='User account'),
            'pwd': openapi.Schema(type=openapi.TYPE_STRING, description='User password'),
            'fullname': openapi.Schema(type=openapi.TYPE_STRING, description='User fullname'),
        }
    ), tags=['User signup'])
    @api_view(['POST'])
    def signup(request):
        '''This method is used for signing up within account ID, fullname and password'''
        try:
            data = request.data

            user = Users(
                acct=data.get('acct'),
                fullname=data.get('fullname'),
                pwd=data.get('pwd'),
            )
            serializer = UsersSerializer(data=data)

            if serializer.is_valid():
                user.pwd = make_password(data.get('pwd'))
                try:
                    session.add(user)
                    session.commit()
                except IntegrityError:
                    # If duplicate primary detected, rollback transaction procedure
                    session.rollback()
                    return JsonResponse({
                        'status': -1,
                        'message': 'Cannot create due to duplicated account ID'
                    },
                        status=status.HTTP_422_UNPROCESSABLE_ENTITY)

                except Exception as e:
                    # Other error cases occur, rollback as well
                    session.rollback()
                    raise Exception

                return JsonResponse({
                    'status': 0,
                },
                    status=status.HTTP_201_CREATED)
            else:
                raise Exception
        except Exception as e:
            return JsonResponse({
                'status': -1,
                'message': 'Signup error'
            },
                status=status.HTTP_422_UNPROCESSABLE_ENTITY)

    @swagger_auto_schema(methods=['put'], operation_description="Used for sign in with given data", request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'acct': openapi.Schema(type=openapi.TYPE_STRING, description='User account'),
            'pwd': openapi.Schema(type=openapi.TYPE_STRING, description='User password'),
        }
    ), tags=['User signin'])
    @api_view(['PUT'])
    def signin(request):
        '''This method is used for sign in with given data'''
        try:
            valid_status = 0
            payload = request.data
            user = session.query(Users).filter(
                Users.acct == payload.get('acct')).scalar()

            if user:
                # Check whether password is correct or not
                if check_password(payload.get('pwd'), user.pwd):
                    token = get_tokens_for_user(user)
                    return JsonResponse({
                        'status': 0,
                        'refresh': token.get('refresh'),
                        'token': token.get('access'),
                    }, status=status.HTTP_204_NO_CONTENT)
                else:
                    valid_status = 1
            else:
                valid_status = 2

            if valid_status != 0:
                raise Exception
        except Exception as e:
            # When signin failed, use websocket service to send signin error message
            send_signin_fail(payload)
            
            if valid_status == 1:
                return JsonResponse({
                    'status': -1,
                    'message': 'Invalid password'
                },  status=status.HTTP_401_UNAUTHORIZED)
            elif valid_status == 2:
                return JsonResponse({
                    'status': -1,
                    'message': 'Cannot find target user'
                },  status=status.HTTP_422_UNPROCESSABLE_ENTITY)
            else:
                return JsonResponse({
                    'status': -1,
                    'message': 'Signin error'
                },  status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @swagger_auto_schema(methods=['delete'], operation_description="Delete specified user",  manual_parameters=[
        openapi.Parameter('acct', openapi.IN_PATH,
                          "User account", type=openapi.TYPE_STRING),
    ], tags=['User delete'])
    @api_view(['DELETE'])
    @permission_classes([IsAuthenticated])
    def delete(request, acct):
        '''This method is used to delete specified user'''
        try:
            user = session.query(Users).filter(Users.acct == acct).scalar()

            if user:
                try:
                    session.delete(user)
                    session.commit()
                except:
                    session.rollback()
                    raise Exception

                return JsonResponse({
                    'status': 0
                }, status=status.HTTP_204_NO_CONTENT)
            else:
                raise ObjectDoesNotExist
        except ObjectDoesNotExist as e:
            return JsonResponse({
                'status': -1,
                'message': 'Cannot find target user'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return JsonResponse({
                'status': -1,
                'message': 'Delete error'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @swagger_auto_schema(methods=['put'], operation_description="Update specified user",  manual_parameters=[
        openapi.Parameter('acct', openapi.IN_PATH,
                          "User account", type=openapi.TYPE_STRING),
    ], request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'fullname': openapi.Schema(type=openapi.TYPE_STRING, description='User fullname'),
            'pwd': openapi.Schema(type=openapi.TYPE_STRING, description='User password'),
        }
    ), tags=['User update'])
    @api_view(['PUT'])
    @permission_classes([IsAuthenticated])
    def update(request, acct):
        '''This method is used to update specified user'''
        try:
            payload = request.POST
            user = session.query(Users).get(acct)

            if user:
                serializer = UsersSerializer(user, data=payload, partial=True)
                if serializer.is_valid():
                    try:
                        for k, v in payload.items():
                            if k == 'pwd':
                                setattr(user, k, make_password(v))
                            elif k == 'fullname':
                                setattr(user, k, v)

                        session.commit()
                    except Exception as e:
                        session.rollback()
                        raise Exception

                    return JsonResponse({
                        'status': 0
                    }, status=status.HTTP_204_NO_CONTENT)
                else:
                    raise Exception
            else:
                raise ObjectDoesNotExist
        except ObjectDoesNotExist as e:
            return JsonResponse({
                'status': -1,
                'message': 'Cannot find target user'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return JsonResponse({
                'status': -1,
                'message': 'Update error'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @swagger_auto_schema(methods=['put'], operation_description="Update specified user with fullname",  manual_parameters=[
        openapi.Parameter('acct', openapi.IN_PATH,
                          "User account", type=openapi.TYPE_STRING),
    ], request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'fullname': openapi.Schema(type=openapi.TYPE_STRING, description='User fullname'),
        }
    ), tags=['Update fullname'])
    @api_view(['PUT'])
    @permission_classes([IsAuthenticated])
    def update_fn(request, acct):
        '''This method is used to update specified user with fullname'''
        try:
            payload = request.POST
            user = session.query(Users).get(acct)
            if user:
                # Check payload only contains fullname attribute
                if not ('fullname' in payload and len(payload) == 1):
                    return JsonResponse({
                        'status': -1,
                        'message': 'Request data should contain only fullname field'
                    }, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

                serializer = UsersSerializer(user, data=payload, partial=True)
                if serializer.is_valid():
                    user.fullname = payload.get('fullname')
                    try:
                        session.commit()
                    except:
                        session.rollback()
                        raise Exception
                    return JsonResponse({
                        'status': 0
                    }, status=status.HTTP_204_NO_CONTENT)
                else:
                    raise Exception
            else:
                raise ObjectDoesNotExist
        except ObjectDoesNotExist as e:
            return JsonResponse({
                'status': -1,
                'message': 'Cannot find target user'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return JsonResponse({
                'status': -1,
                'message': 'Update fullname error'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

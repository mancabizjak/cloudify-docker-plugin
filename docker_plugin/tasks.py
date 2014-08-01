import docker

from cloudify import exceptions

import docker_wrapper


_ERR_MSG_NO_IMAGE_SRC = 'Either path or url to image must be given'


def create(ctx):
    client = docker_wrapper.get_client(ctx)
    if ctx.properties.get('image_import', {}).get('src'):
        image = docker_wrapper.import_image(ctx, client)
    elif ctx.properties.get('image_build', {}).get('path'):
        image = docker_wrapper.build_image(ctx, client)
    else:
        ctx.logger.error(_ERR_MSG_NO_IMAGE_SRC)
        raise exceptions.NonRecoverableError(_ERR_MSG_NO_IMAGE_SRC)
    ctx.runtime_properties.update({'image': image})
    docker_wrapper.create_container(ctx, client)


def run(ctx):
    client = docker_wrapper.get_client(ctx)
    docker_wrapper.start_container(ctx, client)
    container = docker_wrapper.get_container_info(ctx, client)
    log_msg = 'Container: {}\nPorts: {}\nTop: {}'.format(
        container['Id'],
        str(container['Ports']),
        docker_wrapper.get_top_info(ctx, client)
    )
    ctx.logger.info(log_msg)


def stop(ctx):
    client = docker_wrapper.get_client(ctx)
    docker_wrapper.stop_container(ctx, client)


def delete(ctx):
    client = docker_wrapper.get_client(ctx)
    container_info = docker_wrapper.inspect_container(ctx, client)
    if container_info and container_info['State']['Running']:
        docker_wrapper.stop_container(ctx, client)
    remove_image = ctx.properties.get('container_remove', {}).pop(
        'remove_image', None
    )
    docker_wrapper.remove_container(ctx, client)
    if remove_image:
        docker_wrapper.remove_image(ctx, client)
# Blender FLIP Fluid Add-on
# Copyright (C) 2019 Ryan L. Guy
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import bpy

from .utils import version_compatibility_utils as vcu

IS_RENDERING = False
IS_FRAME_REQUIRING_RELOAD = False


def __get_domain_properties():
    return bpy.context.scene.flip_fluid.get_domain_properties() 


def __is_domain_set():
    return bpy.context.scene.flip_fluid.get_domain_object() is not None


def __get_current_frame():
    dprops = bpy.context.scene.flip_fluid.get_domain_properties()
    if dprops is None:
        return 0 

    if dprops.render.hold_frame:
        current_frame = dprops.render.hold_frame_number
    else:
        current_frame = bpy.context.scene.frame_current
    return current_frame - bpy.context.scene.flip_fluid_helper.playback_frame_offset


def __get_display_mode():
    if not __is_domain_set():
        return

    dprops = __get_domain_properties()
    if IS_RENDERING:
        mode = dprops.render.render_display
        if not bpy.context.scene.flip_fluid.show_render:
            mode = 'DISPLAY_NONE'
    else:
        mode = dprops.render.viewport_display
        if not bpy.context.scene.flip_fluid.show_viewport:
            mode = 'DISPLAY_NONE'
    return mode


def __update_surface_display_mode():
    dprops = __get_domain_properties()
    surface_cache = dprops.mesh_cache.surface

    display_mode = __get_display_mode()
    if display_mode == 'DISPLAY_FINAL':
        surface_cache.mesh_prefix = ""
        surface_cache.mesh_display_name_prefix = "final_"
        render_blur = IS_RENDERING and dprops.render.render_surface_motion_blur
        surface_cache.enable_motion_blur = render_blur
        surface_cache.motion_blur_scale = dprops.render.surface_motion_blur_scale
    elif display_mode == 'DISPLAY_PREVIEW':
        surface_cache.mesh_prefix = "preview"
        surface_cache.mesh_display_name_prefix = "preview_"
        surface_cache.enable_motion_blur = False
    elif display_mode == 'DISPLAY_NONE':
        surface_cache.mesh_prefix = "none"
        surface_cache.mesh_display_name_prefix = "none_"
        surface_cache.enable_motion_blur = False


def __load_surface_frame(frameno, force_reload=False, depsgraph=None):
    global IS_RENDERING
    if not __is_domain_set():
        return

    __update_surface_display_mode()

    force_load = force_reload or IS_RENDERING
    dprops = __get_domain_properties()
    dprops.mesh_cache.surface.load_frame(frameno, force_load, depsgraph)


def __get_whitewater_display_mode():
    if not __is_domain_set():
        return

    dprops = __get_domain_properties()
    if IS_RENDERING:
        mode = dprops.render.whitewater_render_display
    else:
        mode = dprops.render.whitewater_viewport_display
    return mode


def __get_whitewater_display_percentages():
    dprops = __get_domain_properties()
    rprops = dprops.render

    display_mode = __get_whitewater_display_mode()
    if rprops.whitewater_view_settings_mode == 'VIEW_SETTINGS_WHITEWATER':
        if display_mode == 'DISPLAY_FINAL':
            pct = rprops.render_whitewater_pct
        elif display_mode == 'DISPLAY_PREVIEW':
            pct = rprops.viewport_whitewater_pct
        elif display_mode == 'DISPLAY_NONE':
            pct = 0
        foam_pct = bubble_pct = spray_pct = dust_pct = pct
    else:
        if display_mode == 'DISPLAY_FINAL':
            foam_pct = rprops.render_foam_pct
            bubble_pct = rprops.render_bubble_pct
            spray_pct = rprops.render_spray_pct
            dust_pct = rprops.render_dust_pct
        elif display_mode == 'DISPLAY_PREVIEW':
            foam_pct = rprops.viewport_foam_pct
            bubble_pct = rprops.viewport_bubble_pct
            spray_pct = rprops.viewport_spray_pct
            dust_pct = rprops.viewport_dust_pct
        elif display_mode == 'DISPLAY_NONE':
            foam_pct = bubble_pct = spray_pct = dust_pct = 0

    return foam_pct, bubble_pct, spray_pct, dust_pct


def __update_whitewater_display_mode():
    dprops = __get_domain_properties()
    cache = dprops.mesh_cache

    display_mode = __get_whitewater_display_mode()
    if display_mode == 'DISPLAY_FINAL':
        cache.foam.mesh_prefix = "foam"
        cache.bubble.mesh_prefix = "bubble"
        cache.spray.mesh_prefix = "spray"
        cache.dust.mesh_prefix = "dust"
        cache.foam.mesh_display_name_prefix = "final_"
        cache.bubble.mesh_display_name_prefix = "final_"
        cache.spray.mesh_display_name_prefix = "final_"
        cache.dust.mesh_display_name_prefix = "final_"

        render_blur = IS_RENDERING and dprops.render.render_whitewater_motion_blur
        cache.foam.enable_motion_blur = render_blur
        cache.bubble.enable_motion_blur = render_blur
        cache.spray.enable_motion_blur = render_blur
        cache.dust.enable_motion_blur = render_blur
        cache.foam.motion_blur_scale = dprops.render.whitewater_motion_blur_scale
        cache.bubble.motion_blur_scale = dprops.render.whitewater_motion_blur_scale
        cache.spray.motion_blur_scale = dprops.render.whitewater_motion_blur_scale
        cache.dust.motion_blur_scale = dprops.render.whitewater_motion_blur_scale
    elif display_mode == 'DISPLAY_PREVIEW':
        cache.foam.mesh_prefix = "foam"
        cache.bubble.mesh_prefix = "bubble"
        cache.spray.mesh_prefix = "spray"
        cache.dust.mesh_prefix = "dust"
        cache.foam.mesh_display_name_prefix = "preview_"
        cache.bubble.mesh_display_name_prefix = "preview_"
        cache.spray.mesh_display_name_prefix = "preview_"
        cache.dust.mesh_display_name_prefix = "preview_"
        cache.foam.enable_motion_blur = False
        cache.bubble.enable_motion_blur = False
        cache.spray.enable_motion_blur = False
        cache.dust.enable_motion_blur = False
    elif display_mode == 'DISPLAY_NONE':
        cache.foam.mesh_prefix = "foam_none"
        cache.bubble.mesh_prefix = "bubble_none"
        cache.spray.mesh_prefix = "spray_none"
        cache.dust.mesh_prefix = "dust_none"
        cache.foam.mesh_display_name_prefix = "none_"
        cache.bubble.mesh_display_name_prefix = "none_"
        cache.spray.mesh_display_name_prefix = "none_"
        cache.dust.mesh_display_name_prefix = "none_"
        cache.foam.enable_motion_blur = False
        cache.bubble.enable_motion_blur = False
        cache.spray.enable_motion_blur = False
        cache.dust.enable_motion_blur = False

    foam_pct, bubble_pct, spray_pct, dust_pct = __get_whitewater_display_percentages()
    cache.foam.wwp_import_percentage = foam_pct
    cache.bubble.wwp_import_percentage = bubble_pct
    cache.spray.wwp_import_percentage = spray_pct
    cache.dust.wwp_import_percentage = dust_pct



def __load_whitewater_particle_frame(frameno, force_reload=False, depsgraph=None):
    global IS_RENDERING
    if not __is_domain_set():
        return

    dprops = __get_domain_properties()
    if not dprops.whitewater.enable_whitewater_simulation:
        return

    __update_whitewater_display_mode()

    force_load = force_reload or IS_RENDERING
    dprops.mesh_cache.foam.load_frame(frameno, force_load, depsgraph)
    dprops.mesh_cache.bubble.load_frame(frameno, force_load, depsgraph)
    dprops.mesh_cache.spray.load_frame(frameno, force_load, depsgraph)
    dprops.mesh_cache.dust.load_frame(frameno, force_load, depsgraph)


def __generate_icosphere_geometry():
    # Icosphere with 1 subdivision (20 sides) centred at origin
    verts = [
        (0.0000, 0.0000, -1.0000), (0.7236, -0.5257, -0.4472), (-0.2764, -0.8506, -0.4472),
        (-0.8944, 0.0000, -0.4472), (-0.2764, 0.8506, -0.4472), (0.7236, 0.5257, -0.4472),
        (0.2764, -0.8506, 0.4472), (-0.7236, -0.5257, 0.4472), (-0.7236, 0.5257, 0.4472),
        (0.2764, 0.8506, 0.4472), (0.8944, 0.0000, 0.4472), (0.0000, 0.0000, 1.0000)
    ]
    tris = [
        (0, 1, 2), (1, 0, 5), (0, 2, 3), (0, 3, 4), (0, 4, 5), (1, 5, 10), (2, 1, 6), (3, 2, 7),
        (4, 3, 8), (5, 4, 9), (1, 10, 6), (2, 6, 7), (3, 7, 8), (4, 8, 9), (5, 9, 10), (6, 10, 11),
        (7, 6, 11), (8, 7, 11), (9, 8, 11), (10, 9, 11)
    ]
    return verts, tris


def __generate_cube_geometry():
    # cube with 6 sides centred at origin
    h = 0.5
    verts = [
        (h, h, -h), (h, -h, -h), (-h, -h, -h), (-h, h, -h), (h, h, h), (h, -h, h), (-h, -h, h), (-h, h, h)
    ]
    tris = [
        (0, 1, 2, 3), (4, 7, 6, 5),  (0, 4, 5, 1),  (1, 5, 6, 2),  (2, 6, 7, 3),  (4, 0, 3, 7)
    ]
    return verts, tris


def __get_object_geometry(bl_object):
    verts, faces = [], []
    for v in bl_object.data.vertices:
        verts.append((v.co.x, v.co.y, v.co.z))
    for p in bl_object.data.polygons:
        face = []
        for idx in p.vertices:
            face.append(idx)
        faces.append(tuple(face))
    return verts, faces


def __get_whitewater_particle_object_geometry(whitewater_type):
    dprops = __get_domain_properties()
    rprops = dprops.render

    if whitewater_type == 'FOAM':
        particle_mode = rprops.foam_particle_object_mode
        particle_object_name = rprops.foam_particle_object
    elif whitewater_type == 'BUBBLE':
        particle_mode = rprops.bubble_particle_object_mode
        particle_object_name = rprops.bubble_particle_object
    elif whitewater_type == 'SPRAY':
        particle_mode = rprops.spray_particle_object_mode
        particle_object_name = rprops.spray_particle_object
    elif whitewater_type == 'DUST':
        particle_mode = rprops.dust_particle_object_mode
        particle_object_name = rprops.dust_particle_object

    merge_settings = rprops.whitewater_particle_object_settings_mode == 'WHITEWATER_OBJECT_SETTINGS_WHITEWATER'
    if merge_settings:
            use_builtin_object = rprops.whitewater_particle_object_mode != 'WHITEWATER_PARTICLE_CUSTOM'
            particle_mode = rprops.whitewater_particle_object_mode
    else:
        use_builtin_object = particle_mode != 'WHITEWATER_PARTICLE_CUSTOM'

    if use_builtin_object:
        if particle_mode == 'WHITEWATER_PARTICLE_ICOSPHERE':
            return __generate_icosphere_geometry()
        elif particle_mode == 'WHITEWATER_PARTICLE_CUBE':
            return __generate_cube_geometry()
    else:
        if merge_settings:
            object_name = rprops.whitewater_particle_object
        else:
            object_name = particle_object_name
        bl_object = bpy.data.objects.get(object_name)

        if bl_object is not None:
            return __get_object_geometry(bl_object)
        else:
            return [], []


def __get_whitewater_particle_object_scale(whitewater_type):
    dprops = __get_domain_properties()
    rprops = dprops.render

    if whitewater_type == 'FOAM':
        particle_object_scale = rprops.foam_particle_scale
    elif whitewater_type == 'BUBBLE':
        particle_object_scale = rprops.bubble_particle_scale
    elif whitewater_type == 'SPRAY':
        particle_object_scale = rprops.spray_particle_scale
    elif whitewater_type == 'DUST':
        particle_object_scale = rprops.dust_particle_scale

    if rprops.whitewater_particle_object_settings_mode == 'WHITEWATER_OBJECT_SETTINGS_WHITEWATER':
        return rprops.whitewater_particle_scale
    else:
        return particle_object_scale


def __get_whitewater_particle_object_display_bool(whitewater_type):
    global IS_RENDERING
    dprops = __get_domain_properties()
    rprops = dprops.render

    if whitewater_type == 'FOAM':
        particle_object_viewport_display = not rprops.only_display_foam_in_render
    elif whitewater_type == 'BUBBLE':
        particle_object_viewport_display = not rprops.only_display_bubble_in_render
    elif whitewater_type == 'SPRAY':
        particle_object_viewport_display = not rprops.only_display_spray_in_render
    elif whitewater_type == 'DUST':
        particle_object_viewport_display = not rprops.only_display_dust_in_render

    if rprops.whitewater_particle_object_settings_mode == 'WHITEWATER_OBJECT_SETTINGS_WHITEWATER':
        return (not rprops.only_display_whitewater_in_render) or IS_RENDERING
    else:
        return particle_object_viewport_display or IS_RENDERING


def __load_whitewater_particle_object_frame(frameno, force_reload=False, depsgraph=None):
    global IS_RENDERING
    if not __is_domain_set():
        return

    dprops = __get_domain_properties()
    if not dprops.whitewater.enable_whitewater_simulation:
        return

    foam_verts,   foam_tris =   __get_whitewater_particle_object_geometry("FOAM")
    bubble_verts, bubble_tris = __get_whitewater_particle_object_geometry("BUBBLE")
    spray_verts,  spray_tris =  __get_whitewater_particle_object_geometry("SPRAY")
    dust_verts,   dust_tris =   __get_whitewater_particle_object_geometry("DUST")

    foam_scale =   __get_whitewater_particle_object_scale('FOAM')
    bubble_scale = __get_whitewater_particle_object_scale('BUBBLE')
    spray_scale =  __get_whitewater_particle_object_scale('SPRAY')
    dust_scale =   __get_whitewater_particle_object_scale('DUST')

    display_foam_particle =   __get_whitewater_particle_object_display_bool('FOAM')
    display_bubble_particle = __get_whitewater_particle_object_display_bool('BUBBLE')
    display_spray_particle =  __get_whitewater_particle_object_display_bool('SPRAY')
    display_dust_particle =   __get_whitewater_particle_object_display_bool('DUST')

    force_load = force_reload or IS_RENDERING
    if foam_verts and display_foam_particle:
        dprops.mesh_cache.foam.load_duplivert_object(
                foam_verts, foam_tris,
                foam_scale,
                force_load,
                depsgraph
                )
    else:
        dprops.mesh_cache.foam.unload_duplivert_object()
        
    if bubble_verts and display_bubble_particle:
        dprops.mesh_cache.bubble.load_duplivert_object(
                bubble_verts, bubble_tris,
                bubble_scale,
                force_load,
                depsgraph
                )
    else:
        dprops.mesh_cache.bubble.unload_duplivert_object()

    if spray_verts and display_spray_particle:
        dprops.mesh_cache.spray.load_duplivert_object(
                spray_verts, spray_tris,
                spray_scale,
                force_load,
                depsgraph
                )
    else:
        dprops.mesh_cache.spray.unload_duplivert_object()

    if dust_verts and display_dust_particle:
        dprops.mesh_cache.dust.load_duplivert_object(
                dust_verts, dust_tris,
                dust_scale,
                force_load,
                depsgraph
                )
    else:
        dprops.mesh_cache.dust.unload_duplivert_object()


def __load_whitewater_frame(frameno, force_reload=False, depsgraph=None):
    __load_whitewater_particle_frame(frameno, force_reload, depsgraph)
    __load_whitewater_particle_object_frame(frameno, force_reload, depsgraph)


def __load_fluid_particle_debug_frame(frameno, force_reload=False):
    global IS_RENDERING
    if not __is_domain_set():
        return

    dprops = __get_domain_properties()
    if not dprops.debug.export_fluid_particles:
        return

    force_load = force_reload or IS_RENDERING
    dprops.mesh_cache.gl_particles.load_frame(frameno, force_load)


def __load_obstacle_debug_frame(frameno, force_reload=False):
    global IS_RENDERING
    if not __is_domain_set():
        return

    dprops = __get_domain_properties()
    if not dprops.debug.export_internal_obstacle_mesh:
        return

    force_load = force_reload or IS_RENDERING
    dprops.mesh_cache.obstacle.load_frame(frameno, force_load)


def __load_frame(frameno, force_reload=False, depsgraph=None):
    if not __is_domain_set():
        return

    dprops = __get_domain_properties()
    dprops.mesh_cache.initialize_cache_objects()

    __load_surface_frame(frameno, force_reload, depsgraph)
    __load_whitewater_frame(frameno, force_reload, depsgraph)
    __load_fluid_particle_debug_frame(frameno, force_reload)
    __load_obstacle_debug_frame(frameno, force_reload)


def reload_frame(frameno):
    if not __is_domain_set():
        return
    __load_frame(frameno, True)


def render_init(scene):
    if not __is_domain_set():
        return

    global IS_RENDERING
    IS_RENDERING = True

    dprops = __get_domain_properties()
    dprops.mesh_cache.initialize_cache_objects()

    if dprops.whitewater.enable_whitewater_simulation:
        dprops.mesh_cache.foam.initialize_duplivert_object()
        dprops.mesh_cache.bubble.initialize_duplivert_object()
        dprops.mesh_cache.spray.initialize_duplivert_object()
        dprops.mesh_cache.dust.initialize_duplivert_object()


def render_complete(scene):
    if not __is_domain_set():
        return

    global IS_RENDERING
    global IS_FRAME_REQUIRING_RELOAD
    IS_RENDERING = False
    IS_FRAME_REQUIRING_RELOAD = True

    dprops = __get_domain_properties()
    if dprops.whitewater.enable_whitewater_simulation:
        if not __get_whitewater_particle_object_display_bool('FOAM'):
            dprops.mesh_cache.foam.unload_duplivert_object()
        if not __get_whitewater_particle_object_display_bool('BUBBLE'):
            dprops.mesh_cache.bubble.unload_duplivert_object()
        if not __get_whitewater_particle_object_display_bool('SPRAY'):
            dprops.mesh_cache.spray.unload_duplivert_object()
        if not __get_whitewater_particle_object_display_bool('DUST'):
            dprops.mesh_cache.dust.unload_duplivert_object()


def render_cancel(scene):
    render_complete(scene)


def frame_change_post(scene, depsgraph=None):
    if not __is_domain_set():
        return

    if is_rendering() and vcu.is_blender_28():
        if not scene.render.use_lock_interface:
                print("FLIP FLUIDS WARNING: The Blender interface should be locked during render to prevent render crashes (Blender > Render > Lock Interface).")
        if not vcu.is_blender_281():
            print("FLIP FLUIDS WARNING: Blender 2.80 contains a bug that can cause frequent render crashes and incorrect render results. Blender version 2.81 or higher is recommended.")

    force_reload = False
    frameno = __get_current_frame()
    __load_frame(frameno, force_reload, depsgraph)
    dprops = __get_domain_properties()
    dprops.render.current_frame = frameno


def scene_update_post(scene):
    if not __is_domain_set():
        return

    global IS_FRAME_REQUIRING_RELOAD
    if IS_FRAME_REQUIRING_RELOAD:
        IS_FRAME_REQUIRING_RELOAD = False

        current_frame = __get_current_frame()
        reload_frame(current_frame)
        dprops = bpy.context.scene.flip_fluid.get_domain_properties()
        dprops.render.current_frame = current_frame


def is_rendering():
    global IS_RENDERING
    return IS_RENDERING

-- =====================================================================
-- 04_MIGRACION_SESION3_NOMBRES.sql
-- Sesión 3: Guardar el nombre del usuario al registrarse.
--
-- Los nombres se guardan automaticamente en auth.users dentro de
-- raw_user_meta_data (clave: full_name) cuando la app Flutter llama a
-- signUp(...) con el parametro data: {'full_name': ...}.
--
-- Este script SOLO verifica que los datos quedaron guardados.
-- No es necesario crear tablas nuevas.
-- =====================================================================

-- 1) Ver los usuarios registrados con su nombre (full_name).
select
  u.id,
  u.email,
  u.raw_user_meta_data ->> 'full_name' as nombres,
  u.created_at
from auth.users u
order by u.created_at desc;

-- 2) Solo los que SI tienen nombre registrado.
select
  u.email,
  u.raw_user_meta_data ->> 'full_name' as nombres
from auth.users u
where u.raw_user_meta_data ->> 'full_name' is not null;

-- 3) Actualizar / corregir el nombre de un usuario si hace falta
--    (opcional, reemplaza <ID_DEL_USUARIO> por el id real).
-- update auth.users
-- set raw_user_meta_data =
--       jsonb_set(
--         coalesce(raw_user_meta_data, '{}'::jsonb),
--         '{full_name}',
--         '"Nombre Corregido"'::jsonb
--       )
-- where id = '<ID_DEL_USUARIO>';

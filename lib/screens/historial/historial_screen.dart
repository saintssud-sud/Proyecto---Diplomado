import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../../controllers/historial_controller.dart';
import '../../models/api/modelos_api.dart';
import '../../widgets/vista_con_estados.dart';
import 'grafica_historica_screen.dart';
import 'lista_mediciones_screen.dart';

/// Pantalla 5 — Consultar el historial por variable y rango de fechas.
///
/// Los filtros que se eligen aquí son los que se consultan: la variable y el
/// rango viajan al servicio, y la gráfica y la lista presentan esa misma
/// consulta en lugar de filtrar por su cuenta. El resumen del periodo lo calcula
/// el servicio.
class HistorialScreen extends StatefulWidget {
  const HistorialScreen({super.key});

  @override
  State<HistorialScreen> createState() => _HistorialScreenState();
}

class _HistorialScreenState extends State<HistorialScreen> {
  String _variable = catalogoVariables.first.codigo;
  DateTime? _desde;
  DateTime? _hasta;
  String? _aviso;

  /// Indica si el rango elegido es incoherente.
  ///
  /// Se comprueba en la pantalla para no enviar al servicio una consulta que se
  /// sabe inválida; el servicio la rechazaría igualmente, pero avisar antes
  /// ahorra el viaje y explica el motivo en el momento.
  bool get _rangoIncoherente {
    final DateTime? desde = _desde;
    final DateTime? hasta = _hasta;
    return desde != null && hasta != null && desde.isAfter(hasta);
  }

  Future<void> _elegirFecha(bool esInicio) async {
    final DateTime hoy = DateTime.now();
    final DateTime propuesta = (esInicio ? _desde : _hasta) ?? hoy;
    final DateTime? fecha = await showDatePicker(
      context: context,
      initialDate: propuesta.isAfter(hoy) ? hoy : propuesta,
      firstDate: DateTime(hoy.year - 5),
      lastDate: hoy,
    );
    if (fecha == null) {
      return;
    }
    if (!mounted) {
      return;
    }
    setState(() {
      if (esInicio) {
        _desde = fecha;
      } else {
        _hasta = fecha;
      }
      _aviso = null;
    });
    if (_rangoIncoherente) {
      setState(() {
        _aviso = 'La fecha de inicio es posterior a la de fin: corrija el rango '
            'antes de consultar.';
      });
    }
  }

  /// Arma el filtro con lo elegido en pantalla.
  FiltroHistorial get _filtro =>
      FiltroHistorial(variable: _variable, desde: _desde, hasta: _hasta);

  /// Consulta el historial con los filtros vigentes.
  Future<void> _consultar() async {
    if (_rangoIncoherente) {
      setState(() {
        _aviso = 'La fecha de inicio es posterior a la de fin: corrija el rango '
            'antes de consultar.';
      });
      return;
    }
    setState(() => _aviso = null);
    await context.read<HistorialController>().cargar(filtro: _filtro);
  }

  /// Aplica el filtro y abre la pantalla indicada.
  ///
  /// La consulta se lanza antes de navegar: la pantalla de destino presenta
  /// primero su estado de carga y luego los datos, que es exactamente lo que el
  /// usuario debe ver cuando la información todavía está en camino.
  void _abrir(Widget destino) {
    if (_rangoIncoherente) {
      setState(() {
        _aviso = 'La fecha de inicio es posterior a la de fin: corrija el rango '
            'antes de consultar.';
      });
      return;
    }
    setState(() => _aviso = null);
    context.read<HistorialController>().cargar(filtro: _filtro);
    Navigator.push<void>(
      context,
      MaterialPageRoute<void>(builder: (BuildContext routeContext) => destino),
    );
  }

  String _fmt(DateTime? fecha) {
    if (fecha == null) {
      return 'Sin seleccionar';
    }
    return '${fecha.day.toString().padLeft(2, '0')}/'
        '${fecha.month.toString().padLeft(2, '0')}/${fecha.year}';
  }

  @override
  Widget build(BuildContext context) {
    final HistorialController historial = context.watch<HistorialController>();

    return ListView(
      padding: const EdgeInsets.all(16),
      children: <Widget>[
        const Text(
          'Historial',
          style: TextStyle(fontSize: 22, fontWeight: FontWeight.bold),
        ),
        const SizedBox(height: 8),
        const Text(
          'Consultar historia',
          style: TextStyle(fontSize: 16, fontWeight: FontWeight.w600),
        ),
        const SizedBox(height: 12),
        // Variable a consultar, tomada del catálogo del sistema.
        DropdownButtonFormField<String>(
          initialValue: _variable,
          decoration: const InputDecoration(
            labelText: 'Variable',
            border: OutlineInputBorder(),
          ),
          items: catalogoVariables
              .map(
                (VariableCatalogo variable) => DropdownMenuItem<String>(
                  value: variable.codigo,
                  child: Text(
                    variable.unidad.isEmpty
                        ? variable.nombre
                        : '${variable.nombre} (${variable.unidad})',
                  ),
                ),
              )
              .toList(),
          onChanged: (String? value) {
            if (value != null) {
              setState(() => _variable = value);
            }
          },
        ),
        const SizedBox(height: 14),
        // Rango de fechas.
        Text('Rango de fecha:', style: TextStyle(color: Colors.grey[700])),
        const SizedBox(height: 8),
        Row(
          children: <Widget>[
            Expanded(
              child: OutlinedButton(
                onPressed: () => _elegirFecha(true),
                child: Text('Inicio: ${_fmt(_desde)}'),
              ),
            ),
            const SizedBox(width: 10),
            Expanded(
              child: OutlinedButton(
                onPressed: () => _elegirFecha(false),
                child: Text('Fin: ${_fmt(_hasta)}'),
              ),
            ),
          ],
        ),
        const SizedBox(height: 6),
        Text(
          _desde == null && _hasta == null
              ? 'Sin rango se consulta todo el historial registrado.'
              : 'Variación de fecha',
          style: TextStyle(fontSize: 13, color: Colors.grey[600]),
        ),
        if (_aviso != null) ...<Widget>[
          const SizedBox(height: 8),
          Text(
            _aviso!,
            style: const TextStyle(fontSize: 13, color: Color(0xFFC62828)),
          ),
        ],
        const SizedBox(height: 16),
        // Consulta y accesos a las vistas de detalle.
        Row(
          children: <Widget>[
            Expanded(
              child: FilledButton.icon(
                onPressed: _consultar,
                icon: const Icon(Icons.search),
                label: const Text('Consultar'),
                style: FilledButton.styleFrom(
                  backgroundColor: const Color(0xFF39B54A),
                  foregroundColor: Colors.white,
                ),
              ),
            ),
          ],
        ),
        const SizedBox(height: 10),
        Row(
          children: <Widget>[
            Expanded(
              child: OutlinedButton.icon(
                onPressed: () => _abrir(const GraficaHistoricaScreen()),
                icon: const Icon(Icons.show_chart),
                label: const Text('Ver gráfica'),
              ),
            ),
            const SizedBox(width: 10),
            Expanded(
              child: OutlinedButton.icon(
                onPressed: () => _abrir(const ListaMedicionesScreen()),
                icon: const Icon(Icons.list_alt),
                label: const Text('Mediciones'),
              ),
            ),
          ],
        ),
        const SizedBox(height: 20),
        const Text(
          'Resultado de la consulta',
          style: TextStyle(fontSize: 16, fontWeight: FontWeight.w600),
        ),
        const SizedBox(height: 10),
        if (!historial.seConsulto)
          _Aviso(
            icono: Icons.filter_alt_outlined,
            texto: 'Elija la variable y el rango de fechas, y pulse Consultar '
                'para ver el resumen del periodo.',
          )
        else
          VistaConEstados<ResumenVariable>(
            estado: historial.estado,
            datos: historial.resumen,
            mensajeError: historial.mensajeError,
            errorDeConexion: historial.errorDeConexion,
            alReintentar: _consultar,
            tituloVacio: 'Sin mediciones en el periodo',
            mensajeVacio:
                'No hay mediciones de esta variable en el rango elegido. '
                'Amplíe el rango o registre una medición.',
            alMostrarDatos: (BuildContext contexto, ResumenVariable resumen) {
              return _ResumenDeConsulta(
                resumen: resumen,
                variable: historial.filtro.variable,
              );
            },
          ),
      ],
    );
  }
}

/// Resumen del periodo devuelto por el servicio.
class _ResumenDeConsulta extends StatelessWidget {
  const _ResumenDeConsulta({required this.resumen, required this.variable});

  final ResumenVariable resumen;
  final String variable;

  String _fmt(double valor) => valor == valor.roundToDouble()
      ? valor.toStringAsFixed(0)
      : valor.toStringAsFixed(1);

  @override
  Widget build(BuildContext context) {
    final String sufijo = resumen.unidad.isEmpty ? '' : ' ${resumen.unidad}';
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: <Widget>[
        Text(
          '${nombreDeVariable(variable)} · ${resumen.cantidad} '
          '${resumen.cantidad == 1 ? 'medición' : 'mediciones'}',
          style: const TextStyle(fontSize: 13, color: Colors.grey),
        ),
        const SizedBox(height: 8),
        _ValorActual(
          label: 'Promedio',
          valor: '${_fmt(resumen.promedio)}$sufijo',
        ),
        _ValorActual(label: 'Máximo', valor: '${_fmt(resumen.maximo)}$sufijo'),
        _ValorActual(label: 'Mínimo', valor: '${_fmt(resumen.minimo)}$sufijo'),
      ],
    );
  }
}

/// Aviso informativo para las situaciones que no son un resultado de consulta.
class _Aviso extends StatelessWidget {
  const _Aviso({required this.icono, required this.texto});

  final IconData icono;
  final String texto;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
      ),
      child: Row(
        children: <Widget>[
          Icon(icono, color: Colors.grey[600]),
          const SizedBox(width: 12),
          Expanded(
            child: Text(
              texto,
              style: TextStyle(fontSize: 13, color: Colors.grey[700]),
            ),
          ),
        ],
      ),
    );
  }
}

class _ValorActual extends StatelessWidget {
  const _ValorActual({required this.label, required this.valor});

  final String label;
  final String valor;

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: const EdgeInsets.only(bottom: 8),
      padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
      ),
      child: Row(
        children: <Widget>[
          Expanded(child: Text(label)),
          Text(
            valor,
            style: const TextStyle(
              fontWeight: FontWeight.w600,
              color: Color(0xFF2E7D32),
            ),
          ),
        ],
      ),
    );
  }
}

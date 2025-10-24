"""
Sistema de Estimación de Costos Paramétricos para PTAP
Base de datos local con costos de referencia para Colombia
"""
import json
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class ItemCosto:
    """Representa un ítem de costo"""
    codigo: str
    descripcion: str
    unidad: str
    precio_unitario: float  # COP (pesos colombianos)
    fuente: str
    fecha_actualizacion: str


class BaseDatosCostos:
    """Base de datos local de costos de construcción"""
    
    def __init__(self, archivo_bd: Optional[Path] = None):
        self.archivo_bd = archivo_bd or Path(__file__).parent / "data" / "costos_referencia.json"
        self.costos = self._cargar_base_datos()
    
    def _cargar_base_datos(self) -> Dict[str, ItemCosto]:
        """Carga la base de datos de costos"""
        if self.archivo_bd.exists():
            with open(self.archivo_bd, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return {k: ItemCosto(**v) for k, v in data.items()}
        else:
            # Crear base de datos inicial con valores de referencia
            return self._crear_base_datos_inicial()
    
    def _crear_base_datos_inicial(self) -> Dict[str, ItemCosto]:
        """Crea base de datos inicial con costos de referencia 2024"""
        costos_base = {
            # Movimiento de tierras
            "exc_manual": ItemCosto(
                "exc_manual", "Excavación manual en tierra", "m³",
                45000, "Promedio mercado Colombia 2024", "2024-01"
            ),
            "exc_mecanica": ItemCosto(
                "exc_mecanica", "Excavación mecánica", "m³",
                25000, "Promedio mercado Colombia 2024", "2024-01"
            ),
            "relleno_comp": ItemCosto(
                "relleno_comp", "Relleno compactado", "m³",
                35000, "Promedio mercado Colombia 2024", "2024-01"
            ),
            
            # Concreto y acero
            "conc_3000_psi": ItemCosto(
                "conc_3000_psi", "Concreto 3000 PSI", "m³",
                450000, "Promedio mercado Colombia 2024", "2024-01"
            ),
            "conc_4000_psi": ItemCosto(
                "conc_4000_psi", "Concreto 4000 PSI", "m³",
                520000, "Promedio mercado Colombia 2024", "2024-01"
            ),
            "acero_ref": ItemCosto(
                "acero_ref", "Acero de refuerzo", "kg",
                5500, "Promedio mercado Colombia 2024", "2024-01"
            ),
            
            # Tuberías y accesorios
            "tuberia_pvc_200": ItemCosto(
                "tuberia_pvc_200", "Tubería PVC 200mm", "m",
                65000, "Promedio mercado Colombia 2024", "2024-01"
            ),
            "tuberia_pvc_300": ItemCosto(
                "tuberia_pvc_300", "Tubería PVC 300mm", "m",
                95000, "Promedio mercado Colombia 2024", "2024-01"
            ),
            "valvula_compuerta_200": ItemCosto(
                "valvula_compuerta_200", "Válvula compuerta 200mm", "und",
                850000, "Promedio mercado Colombia 2024", "2024-01"
            ),
            
            # Equipos electromecánicos
            "bomba_centrifuga_5hp": ItemCosto(
                "bomba_centrifuga_5hp", "Bomba centrífuga 5 HP", "und",
                3500000, "Promedio mercado Colombia 2024", "2024-01"
            ),
            "dosificador_quimico": ItemCosto(
                "dosificador_quimico", "Dosificador químico", "und",
                8500000, "Promedio mercado Colombia 2024", "2024-01"
            ),
            
            # Medios filtrantes
            "arena_filtrante": ItemCosto(
                "arena_filtrante", "Arena filtrante lavada", "m³",
                180000, "Promedio mercado Colombia 2024", "2024-01"
            ),
            "antracita": ItemCosto(
                "antracita", "Antracita filtrante", "m³",
                450000, "Promedio mercado Colombia 2024", "2024-01"
            ),
            "grava": ItemCosto(
                "grava", "Grava soporte", "m³",
                75000, "Promedio mercado Colombia 2024", "2024-01"
            ),
            
            # Químicos (precio anual estimado)
            "sulfato_aluminio": ItemCosto(
                "sulfato_aluminio", "Sulfato de aluminio", "kg",
                1200, "Promedio mercado Colombia 2024", "2024-01"
            ),
            "cloro_gas": ItemCosto(
                "cloro_gas", "Cloro gas", "kg",
                4500, "Promedio mercado Colombia 2024", "2024-01"
            ),
            "hipoclorito_sodio": ItemCosto(
                "hipoclorito_sodio", "Hipoclorito de sodio 10%", "L",
                2500, "Promedio mercado Colombia 2024", "2024-01"
            ),
            "polimero": ItemCosto(
                "polimero", "Polímero floculante", "kg",
                15000, "Promedio mercado Colombia 2024", "2024-01"
            ),
            
            # Mano de obra
            "operador_ptap": ItemCosto(
                "operador_ptap", "Operador PTAP", "mes",
                1800000, "SMLV Colombia 2024", "2024-01"
            ),
            "supervisor": ItemCosto(
                "supervisor", "Supervisor técnico", "mes",
                3500000, "Promedio mercado Colombia 2024", "2024-01"
            ),
            
            # Energía
            "energia_electrica": ItemCosto(
                "energia_electrica", "Energía eléctrica", "kWh",
                650, "Promedio Colombia 2024", "2024-01"
            ),
        }
        
        # Guardar base de datos
        self.archivo_bd.parent.mkdir(parents=True, exist_ok=True)
        with open(self.archivo_bd, 'w', encoding='utf-8') as f:
            json.dump({k: asdict(v) for k, v in costos_base.items()}, f, indent=2, ensure_ascii=False)
        
        return costos_base
    
    def obtener_costo(self, codigo: str) -> Optional[ItemCosto]:
        """Obtiene un ítem de costo por código"""
        return self.costos.get(codigo)
    
    def actualizar_costo(self, codigo: str, precio_unitario: float, fuente: str = "Actualización manual"):
        """Actualiza el precio de un ítem"""
        if codigo in self.costos:
            self.costos[codigo].precio_unitario = precio_unitario
            self.costos[codigo].fuente = fuente
            self.costos[codigo].fecha_actualizacion = datetime.now().strftime("%Y-%m")
            self._guardar_base_datos()
    
    def _guardar_base_datos(self):
        """Guarda la base de datos en archivo JSON"""
        with open(self.archivo_bd, 'w', encoding='utf-8') as f:
            json.dump({k: asdict(v) for k, v in self.costos.items()}, f, indent=2, ensure_ascii=False)


class EstimadorCostos:
    """Estimador paramétrico de costos CAPEX y OPEX"""
    
    def __init__(self):
        self.bd_costos = BaseDatosCostos()
    
    def estimar_capex(self, diseño: dict) -> dict:
        """Estima costos de inversión (CAPEX)"""
        
        caudal = diseño.get('caudal', 50)  # L/s
        
        # Estimación de volúmenes de obra civil
        costos_obra_civil = self._estimar_obra_civil(caudal)
        
        # Estimación de equipos
        costos_equipos = self._estimar_equipos(diseño)
        
        # Estimación de tuberías
        costos_tuberias = self._estimar_tuberias(caudal)
        
        # Estimación de medios filtrantes
        costos_medios = self._estimar_medios_filtrantes(diseño)
        
        # Subtotales
        subtotal_directo = (
            costos_obra_civil['total'] +
            costos_equipos['total'] +
            costos_tuberias['total'] +
            costos_medios['total']
        )
        
        # Costos indirectos (25% típico)
        costos_indirectos = subtotal_directo * 0.25
        
        # Imprevistos (10%)
        imprevistos = subtotal_directo * 0.10
        
        # Total CAPEX
        total_capex = subtotal_directo + costos_indirectos + imprevistos
        
        return {
            'obra_civil': costos_obra_civil,
            'equipos': costos_equipos,
            'tuberias': costos_tuberias,
            'medios_filtrantes': costos_medios,
            'subtotal_directo': subtotal_directo,
            'costos_indirectos': costos_indirectos,
            'imprevistos': imprevistos,
            'total_capex': total_capex,
            'costo_unitario_ls': total_capex / caudal,  # COP por L/s
            'moneda': 'COP',
            'fecha_estimacion': datetime.now().isoformat()
        }
    
    def _estimar_obra_civil(self, caudal: float) -> dict:
        """Estima costos de obra civil"""
        
        # Volúmenes paramétricos basados en caudal
        vol_excavacion = caudal * 15  # m³
        vol_concreto = caudal * 3  # m³
        peso_acero = vol_concreto * 100  # kg
        
        exc = self.bd_costos.obtener_costo('exc_mecanica')
        conc = self.bd_costos.obtener_costo('conc_3000_psi')
        acero = self.bd_costos.obtener_costo('acero_ref')
        
        costo_excavacion = vol_excavacion * exc.precio_unitario
        costo_concreto = vol_concreto * conc.precio_unitario
        costo_acero = peso_acero * acero.precio_unitario
        
        return {
            'excavacion': {'cantidad': vol_excavacion, 'unidad': 'm³', 'costo': costo_excavacion},
            'concreto': {'cantidad': vol_concreto, 'unidad': 'm³', 'costo': costo_concreto},
            'acero': {'cantidad': peso_acero, 'unidad': 'kg', 'costo': costo_acero},
            'total': costo_excavacion + costo_concreto + costo_acero
        }
    
    def _estimar_equipos(self, diseño: dict) -> dict:
        """Estima costos de equipos electromecánicos"""
        
        # Dosificadores de químicos
        dosif = self.bd_costos.obtener_costo('dosificador_quimico')
        num_dosificadores = 2  # Coagulante + desinfectante
        costo_dosificadores = num_dosificadores * dosif.precio_unitario
        
        # Bombas (opcional, dependiendo del diseño)
        bomba = self.bd_costos.obtener_costo('bomba_centrifuga_5hp')
        num_bombas = 2  # 1 operando + 1 standby
        costo_bombas = num_bombas * bomba.precio_unitario
        
        return {
            'dosificadores': {'cantidad': num_dosificadores, 'unidad': 'und', 'costo': costo_dosificadores},
            'bombas': {'cantidad': num_bombas, 'unidad': 'und', 'costo': costo_bombas},
            'total': costo_dosificadores + costo_bombas
        }
    
    def _estimar_tuberias(self, caudal: float) -> dict:
        """Estima costos de tuberías y accesorios"""
        
        # Longitud paramétrica
        longitud_tuberia = caudal * 5  # m
        
        tub = self.bd_costos.obtener_costo('tuberia_pvc_300')
        costo_tuberia = longitud_tuberia * tub.precio_unitario
        
        # Válvulas
        valv = self.bd_costos.obtener_costo('valvula_compuerta_200')
        num_valvulas = 8
        costo_valvulas = num_valvulas * valv.precio_unitario
        
        return {
            'tuberia': {'cantidad': longitud_tuberia, 'unidad': 'm', 'costo': costo_tuberia},
            'valvulas': {'cantidad': num_valvulas, 'unidad': 'und', 'costo': costo_valvulas},
            'total': costo_tuberia + costo_valvulas
        }
    
    def _estimar_medios_filtrantes(self, diseño: dict) -> dict:
        """Estima costos de medios filtrantes"""
        
        filtracion = diseño.get('filtracion', {})
        area_filtracion = filtracion.get('area_filtracion', 20)  # m²
        
        arena = self.bd_costos.obtener_costo('arena_filtrante')
        grava = self.bd_costos.obtener_costo('grava')
        
        vol_arena = area_filtracion * 0.7  # m³
        vol_grava = area_filtracion * 0.3  # m³
        
        costo_arena = vol_arena * arena.precio_unitario
        costo_grava = vol_grava * grava.precio_unitario
        
        return {
            'arena': {'cantidad': vol_arena, 'unidad': 'm³', 'costo': costo_arena},
            'grava': {'cantidad': vol_grava, 'unidad': 'm³', 'costo': costo_grava},
            'total': costo_arena + costo_grava
        }
    
    def estimar_opex(self, diseño: dict, caudal_m3_dia: float) -> dict:
        """Estima costos de operación anuales (OPEX)"""
        
        # Químicos
        costos_quimicos = self._estimar_costos_quimicos(diseño, caudal_m3_dia)
        
        # Energía
        costos_energia = self._estimar_costos_energia(caudal_m3_dia)
        
        # Personal
        costos_personal = self._estimar_costos_personal()
        
        # Mantenimiento (5% del CAPEX anual)
        capex = self.estimar_capex(diseño)['total_capex']
        mantenimiento = capex * 0.05
        
        # Total OPEX anual
        total_opex_anual = (
            costos_quimicos['total_anual'] +
            costos_energia['total_anual'] +
            costos_personal['total_anual'] +
            mantenimiento
        )
        
        # Costo por m³ tratado
        m3_año = caudal_m3_dia * 365
        costo_m3 = total_opex_anual / m3_año if m3_año > 0 else 0
        
        return {
            'quimicos': costos_quimicos,
            'energia': costos_energia,
            'personal': costos_personal,
            'mantenimiento': {'costo_anual': mantenimiento},
            'total_opex_anual': total_opex_anual,
            'costo_por_m3': costo_m3,
            'moneda': 'COP',
            'fecha_estimacion': datetime.now().isoformat()
        }
    
    def _estimar_costos_quimicos(self, diseño: dict, caudal_m3_dia: float) -> dict:
        """Estima costos anuales de químicos"""
        
        # Coagulante
        dosis_coag = diseño.get('mezcla_rapida', {}).get('dosis_coagulante', 25)  # mg/L
        kg_coag_dia = (dosis_coag / 1000) * caudal_m3_dia
        kg_coag_año = kg_coag_dia * 365
        
        coag = self.bd_costos.obtener_costo('sulfato_aluminio')
        costo_coag = kg_coag_año * coag.precio_unitario
        
        # Desinfectante (cloro)
        dosis_cloro = diseño.get('desinfeccion', {}).get('dosis_cloro', 2.5)  # mg/L
        kg_cloro_dia = (dosis_cloro / 1000) * caudal_m3_dia
        kg_cloro_año = kg_cloro_dia * 365
        
        cloro = self.bd_costos.obtener_costo('cloro_gas')
        costo_cloro = kg_cloro_año * cloro.precio_unitario
        
        return {
            'coagulante': {'cantidad_anual': kg_coag_año, 'unidad': 'kg', 'costo': costo_coag},
            'cloro': {'cantidad_anual': kg_cloro_año, 'unidad': 'kg', 'costo': costo_cloro},
            'total_anual': costo_coag + costo_cloro
        }
    
    def _estimar_costos_energia(self, caudal_m3_dia: float) -> dict:
        """Estima costos anuales de energía eléctrica"""
        
        # Consumo estimado: 0.05 kWh/m³ (plantas pequeñas/medianas)
        kwh_m3 = 0.05
        kwh_dia = caudal_m3_dia * kwh_m3
        kwh_año = kwh_dia * 365
        
        energia = self.bd_costos.obtener_costo('energia_electrica')
        costo_energia = kwh_año * energia.precio_unitario
        
        return {
            'consumo_anual': {'cantidad': kwh_año, 'unidad': 'kWh', 'costo': costo_energia},
            'total_anual': costo_energia
        }
    
    def _estimar_costos_personal(self) -> dict:
        """Estima costos anuales de personal"""
        
        oper = self.bd_costos.obtener_costo('operador_ptap')
        superv = self.bd_costos.obtener_costo('supervisor')
        
        # 2 operadores + 1 supervisor
        num_operadores = 2
        num_supervisores = 1
        
        costo_oper = num_operadores * oper.precio_unitario * 12
        costo_superv = num_supervisores * superv.precio_unitario * 12
        
        return {
            'operadores': {'cantidad': num_operadores, 'costo_anual': costo_oper},
            'supervisores': {'cantidad': num_supervisores, 'costo_anual': costo_superv},
            'total_anual': costo_oper + costo_superv
        }
    
    def analisis_financiero_completo(self, diseño: dict, tasa_descuento: float = 0.08) -> dict:
        """Análisis financiero completo con VPN, TIR, periodo de recuperación"""
        
        caudal_ls = diseño.get('caudal', 50)
        caudal_m3_dia = (caudal_ls * 86.4)  # L/s a m³/día
        
        capex = self.estimar_capex(diseño)
        opex = self.estimar_opex(diseño, caudal_m3_dia)
        
        # Horizonte de evaluación (25 años típico)
        años = 25
        
        # VPN (Valor Presente Neto) de costos
        vpn_opex = sum([opex['total_opex_anual'] / ((1 + tasa_descuento) ** t) for t in range(1, años + 1)])
        vpn_total = capex['total_capex'] + vpn_opex
        
        # Costo nivelado por m³
        m3_total_25años = caudal_m3_dia * 365 * años
        costo_nivelado_m3 = vpn_total / m3_total_25años if m3_total_25años > 0 else 0
        
        return {
            'capex': capex['total_capex'],
            'opex_anual': opex['total_opex_anual'],
            'vpn_opex_25años': vpn_opex,
            'vpn_total_25años': vpn_total,
            'costo_nivelado_m3': costo_nivelado_m3,
            'tasa_descuento': tasa_descuento,
            'horizonte_años': años,
            'moneda': 'COP'
        }

/**
 * Карта lucide-react иконок по строковому ключу.
 *
 * Должна совпадать с ICON_CHOICES в backend/apps/content/models.py.
 * Если врач выбрал неизвестную иконку — на фронте подставляется DEFAULT_ICON.
 */

import {
  Activity,
  AlertTriangle,
  Award,
  BadgeCheck,
  Building2,
  Calendar,
  CalendarCheck,
  CalendarDays,
  Car,
  CarTaxiFront,
  CheckCheck,
  CheckCircle,
  ClipboardList,
  Clock,
  FileText,
  GraduationCap,
  Heart,
  HeartPulse,
  HelpCircle,
  Hospital,
  Info,
  ListChecks,
  type LucideIcon,
  Mail,
  Map,
  MapPin,
  MessageCircle,
  MessageCircleHeart,
  MessageSquare,
  Microscope,
  Phone,
  Pill,
  ScrollText,
  Send,
  ShieldCheck,
  Smile,
  Sparkles,
  Stethoscope,
  Syringe,
  TestTube,
  ThumbsUp,
  Train,
  TrendingUp,
  Users,
} from "lucide-react";

export const ICON_MAP: Record<string, LucideIcon> = {
  // Медицина
  stethoscope: Stethoscope,
  hospital: Hospital,
  pill: Pill,
  syringe: Syringe,
  heart: Heart,
  heart_pulse: HeartPulse,
  activity: Activity,
  microscope: Microscope,
  test_tube: TestTube,
  // Календарь и время
  calendar: Calendar,
  calendar_check: CalendarCheck,
  calendar_days: CalendarDays,
  clock: Clock,
  // Сообщения
  message_square: MessageSquare,
  message_circle: MessageCircle,
  message_circle_heart: MessageCircleHeart,
  send: Send,
  phone: Phone,
  mail: Mail,
  users: Users,
  // Документы
  clipboard_list: ClipboardList,
  file_text: FileText,
  scroll_text: ScrollText,
  list_checks: ListChecks,
  check_check: CheckCheck,
  check_circle: CheckCircle,
  // Защита, награды
  shield_check: ShieldCheck,
  award: Award,
  badge_check: BadgeCheck,
  graduation_cap: GraduationCap,
  trending_up: TrendingUp,
  sparkles: Sparkles,
  // Локация и транспорт
  map_pin: MapPin,
  map: Map,
  train: Train,
  car: Car,
  car_taxi_front: CarTaxiFront,
  building_2: Building2,
  // Прочее
  info: Info,
  help_circle: HelpCircle,
  alert_triangle: AlertTriangle,
  thumbs_up: ThumbsUp,
  smile: Smile,
};

export const DEFAULT_ICON: LucideIcon = Sparkles;

export function resolveIcon(key: string | null | undefined): LucideIcon {
  if (!key) return DEFAULT_ICON;
  return ICON_MAP[key] ?? DEFAULT_ICON;
}

# -*- coding: utf-8 -*-
# dreamtools-dreamgeeker/date_manager.py

"""
Module de Gestion des Dates
=============================

Fournit un ensemble de fonctions utilitaires pour manipuler les dates et heures en Python,
avec gestion des timezones, formats de dates, jours fériés et conversions diverses.

Constantes globales
-------------------
I_MON, I_TUES, I_WED, I_THU, I_FRI, I_SAT, I_SUN : Index numériques des jours de la semaine.

Timezones préconfigurées : tz_fr (Europe/Paris), tz_cay (America/Cayenne), tz_utc (UTC).

Formats de date disponibles :
- FR_FORMAT_DATE : '%d.%m.%Y'
- FR_FORMAT_DTIME : '%d-%m-%Y %H:%M:%S'
- FR_FORMAT_RSS_2 : '%a, %d %b %Y %H:%M:%S %z'
- FR_FORMAT_RSS_SHORT : '%a %d %b %Y'
- FR_FORMAT_RSS_ATOM : '%Y-%m-%dT%H:%M:%SZ'

Formats d'identifiants :
- FRM_ISO : format ISO 8601
- FRM_TIMESTAMP : timestamp UNIX

Toutes les fonctions respectent la timezone et peuvent travailler avec des objets `date`, `datetime`, ou `timestamp`.
"""

import locale
from datetime import datetime, timedelta, date

import pytz
from tzlocal import get_localzone_name

I_MON, I_TUES, I_WED, I_THU, I_FRI, I_SAT, I_SUN = 1, 2, 3, 4, 5, 6, 0

locale.setlocale(locale.LC_TIME, 'fr_FR.utf8')

nap_days_dc = {}

FR_FORMAT_DATE = '%d.%m.%Y'  # correction ici
FR_FORMAT_DTIME = '%d-%m-%Y %H:%M:%S'  # correction ici
FR_FORMAT_RSS_2 = '%a, %d %b %Y %H:%M:%S %z'  # correction ici
FR_FORMAT_RSS_SHORT = '%a %d %b %Y'  # correction ici
FR_FORMAT_RSS_ATOM = '%Y-%m-%dT%H:%M:%SZ'  # correction ici

FRM_ISO = 'iso'
FRM_TIMESTAMP = 'ts'


def get_timezone(name=None):
    if name:
        return pytz.timezone(name)
    return pytz.timezone(get_localzone_name())


tz_cay = get_timezone('America/Cayenne')
tz_fr = get_timezone('Europe/Paris')
tz_utc = pytz.UTC
tz_local = get_timezone()


def dte_to_dtime(dtime: date, ptz: pytz.timezone = tz_utc, force_midnight=False) -> datetime:
    """
    Convertit un objet `date` en `datetime` à minuit (00:00:00).

    Si l'objet est déjà un `datetime`, il est renvoyé tel quel.

    :param dtime: Date ou datetime à convertir
    :param ptz: Fuseau horaire à appliquer si conversion nécessaire (défaut : UTC)
    :param force_midnight: Si True, positionne systématiquement à minuit
    :return: Objet datetime timezone-aware

    :Exemple:
        >>> dte_to_dtime(date(2025, 1, 1))
        datetime.datetime(2025, 1, 1, 0, 0, tzinfo=<UTC>)
    """

    if isinstance(dtime, date) and not isinstance(dtime, datetime):
        dtime = datetime.combine(dtime, datetime.min.time())
        dtime = set_timezone(dtime, ptz=ptz)
    elif force_midnight:
        dtime = datetime.combine(dtime, datetime.min.time())

    return dtime


def get_midnight_dtime(dtime: date | None = None, ptz=tz_utc) -> datetime:
    """
    Renvoie un datetime positionné à minuit du jour indiqué (ou aujourd'hui).

    :param dtime: Date ou None (utilise aujourd'hui si None)
    :param ptz: Fuseau horaire à appliquer (défaut : UTC)
    :return: Datetime à 00:00:00
    """
    return dte_to_dtime(dtime or get_now_dtime(ptz), ptz, force_midnight=True)


def get_now_dtime(ptz=tz_utc) -> datetime:
    """
    Renvoie la date et l'heure actuelle avec timezone.

    :param ptz: Fuseau horaire à utiliser (défaut : UTC)
    :return: Datetime actuel timezone-aware
    """
    return datetime.now(ptz)


def get_now_str(ptz=tz_utc, fm=FR_FORMAT_DTIME) -> str:
    """
    Renvoie la date et l'heure actuelle formatée.

    :param ptz: Fuseau horaire à utiliser (défaut : UTC)
    :param fm: Format de la date (strptime)
    :return: Chaîne formatée

    :Exemple:
        >>> get_now_str()
        '12-07-2025 10:34:00'
    """

    return get_dtime_str(get_now_dtime(ptz), fm=fm)


def get_today_str(ptz=tz_utc, fm=FR_FORMAT_DATE) -> str:
    """
    Renvoie la date actuelle formatée sans heure.

    :param ptz: Fuseau horaire à utiliser (défaut : UTC)
    :param fm: Format de date (ex : '%d/%m/%Y')
    :return: Chaîne de date
    """
    return get_now_str(ptz, fm=fm)


def get_dtime_str(dtime: datetime | date | None = None, ptz: pytz.timezone = tz_utc,
                  fm: str = FRM_ISO) -> str | datetime:
    """
    Formate un datetime ou une date selon le format demandé.

    :param dtime: Date ou datetime à formater (None = maintenant)
    :param ptz: Fuseau horaire à appliquer (défaut : UTC)
    :param fm: Format de sortie ('iso' pour isoformat ou format strptime)
    :return: Chaîne formatée ou datetime
    """
    dtime = get_now_dtime(ptz) if dtime is None else dte_to_dtime(dtime, ptz)

    if fm == FRM_ISO:
        return dtime.isoformat()

    return dtime.strftime(fm)


def set_timezone(dtime: datetime, ptz=tz_utc) -> datetime:
    """
    Applique une timezone à un datetime naïf ou convertit entre timezones.

    :param dtime: Datetime à traiter
    :param ptz: Timezone cible (défaut : UTC)
    :return: Datetime
    """
    if dtime.tzinfo is None:
        return ptz.localize(dtime)
    elif dtime.tzinfo != ptz:
        return dtime.astimezone(ptz)
    else:
        return dtime


def dtime_to_local(dtime: datetime) -> datetime:
    """
    Convertit un datetime en datetime local .

    :param dtime: Datetime en UTC
    :return: Datetime dans la timezone locale
    """
    return set_timezone(dtime, tz_local)


def dtime_to_utc(dtime: datetime) -> datetime:
    """
    Convertit un datetime en datetime utc .

    :param dtime: Datetime en UTC
    :return: Datetime dans la timezone locale
    """
    return set_timezone(dtime, tz_local)


def dtime_to_fr(dtime: datetime) -> datetime:
    """
    Convertit un datetime en datetime france .

    :param dtime: Datetime en UTC
    :return: Datetime dans la timezone locale
    """
    return set_timezone(dtime, tz_local)


def get_dtime_ts(dtime: datetime | date | None = None, ptz: pytz.timezone = tz_utc) -> int:
    """
    Retourne le timestamp (secondes depuis Epoch) d'une date donnée.

    :param dtime: objet date, datetime ou None
    :param ptz: timezone de référence (défaut : UTC)
    :return: timestamp (int)
    """
    dtime = get_now_dtime(ptz) if dtime is None else dte_to_dtime(dtime, ptz)
    return int(dtime.timestamp())


def get_midnight_ts(dtime: datetime | date | None = None, ptz: pytz.timezone = tz_utc) -> int:
    """
    Retourne le timestamp correspondant à minuit du jour spécifié.

    :param dtime: Objet date ou datetime ou None
    :param ptz: timezone de référence
    :return: timestamp à 00:00 du jour
    """
    dtime = get_midnight_dtime(dtime, ptz)
    return int(dtime.timestamp())


def get_yesterday_ts(dtime: datetime | date | None = None, ptz: pytz.timezone = tz_utc) -> int:
    """
    Retourne le timestamp à minuit du jour précédent la date spécifiée.

    :param dtime: Date de référence ou None (par défaut : aujourd'hui)
    :param ptz: timezone de référence
    :return: timestamp à minuit du jour précédent
    """
    dtime = get_midnight_dtime(dtime, ptz)
    dtime = dtime_add_days(dtime, -1)

    return int(dtime.timestamp())


def ts_until_midnight(dtime: datetime | date | None = None, ptz: pytz.timezone = tz_utc) -> int:
    """
    Retourne le nombre de secondes jusqu'à minuit suivant la date donnée.

    :param dtime: date ou datetime (None = maintenant)
    :param ptz: timezone cible
    :return: nombre de secondes jusqu'à la prochaine minuit
    """
    dtime = get_midnight_dtime(dtime, ptz)
    today = get_midnight_ts(dtime, ptz)
    tonight = dtime_add_days(dtime)

    return int(tonight.timestamp() - today)


def utcnow_iso() -> str:
    """
    Retourne la date/heure actuelle UTC au format ISO 8601.

    :return str: date au format ISO
    """
    return get_dtime_str(ptz=tz_utc)


def utcnow_ts() -> int:
    """
    Retourne la date/heure actuelle UTC en timestamp (secondes).

    :return: timestamp UTC (int)
    """
    return get_dtime_ts(ptz=tz_utc)


def utcnow_str() -> str:
    """
    Retourne la date/heure actuelle UTC au format ISO.

    :return: chaîne de date ISO UTC (str)
    """
    return get_now_str(ptz=tz_utc, fm=FRM_ISO)


def set_dte(p_year, p_month, p_day) -> date:
    """
    Crée un objet `date` à partir de valeurs numériques.

    :param p_year: année (int)
    :param p_month: mois (int)
    :param p_day: jour (int)
    :return: objet date
    """
    return date(p_year, p_month, p_day)


def set_dtime(p_year, p_month, p_day, ptz: pytz.timezone = tz_utc) -> datetime:
    """
    Crée un objet `datetime` à partir d'une date numérique, positionnée à minuit.

    :param p_year: année (int)
    :param p_month: mois (int)
    :param p_day: jour (int)
    :param ptz: timezone (défaut UTC)
    :return: objet datetime timezone-aware à 00:00
    """
    dte = set_dte(p_year, p_month, p_day)
    return dte_to_dtime(dte, ptz)


def ts_to_dtime(ts) -> datetime:
    """
    Convertit un timestamp en objet `datetime`.

    :param ts: timestamp (int ou float)
    :return: datetime correspondant
    """
    return datetime.fromtimestamp(int(ts))  # => renvoie datetime


def ts_to_str(ts, ptz: pytz.timezone = tz_utc, fm=FR_FORMAT_DTIME):
    """
    Convertit un timestamp en chaîne formatée.

    :param ts: timestamp à convertir
    :param ptz: timezone pour conversion
    :param fm: format d'affichage (strftime)
    :return: chaîne de caractères représentant la date
    """
    dtime = ts_to_dtime(ts)
    return get_dtime_str(dtime, ptz, fm)


def str_to_dtime(s_dte: str, ptz=tz_utc, fm=FR_FORMAT_DTIME):
    """
    Convertit une chaîne formatée en objet `datetime` timezone-aware.

    :param s_dte: chaîne de date à convertir
    :param ptz: timezone cible
    :param fm: format de la chaîne (par défaut : '%d-%m-%Y %H:%M:%S')
    :return: objet datetime ou None si invalide

    :Exemple:
        >>> str_to_dtime('24-02-1976 16:45')
        datetime.datetime(1976, 2, 24, 16, 45, tzinfo=...)
    """
    dtime = datetime.strptime(s_dte, fm)
    return set_timezone(dtime, ptz)


def paques(y):
    """
    Calcule les dates des fêtes mobiles basées sur Pâques pour une année donnée.

    Retourne une liste avec :
    - dimanche de Pâques
    - lundi de Pâques (le lendemain)
    - jeudi de l'Ascension (39 jours après Pâques)
    - Pentecôte (49 jours après le lundi de Pâques)

    :param y: année de référence
    :return: liste de datetime timezone-aware (UTC)

    :Exemple:
        >>> paques(2025)
        [datetime.datetime(2025, 4, 20, 0, 0, tzinfo=...), datetime.datetime(2025, 4, 21, 0, 0, tzinfo=...), datetime.datetime(2025, 5, 29, 0, 0, tzinfo=...), datetime.datetime(2025, 6, 9, 0, 0, tzinfo=...)]
    """

    a = y // 100
    b = y % 100

    c = (3 * (a + 25)) // 4
    d = (3 * (a + 25)) % 4
    e = (8 * (a + 11)) // 25

    f = (5 * a + b) % 19
    g = (19 * f + c - e) % 30
    h = (f + 11 * g) // 319

    j = (60 * (5 - d) + b) // 4
    k = (60 * (5 - d) + b) % 4

    m = (2 * j - k - g + h) % 7
    n = (g - h + m + 114) // 31
    p = (g - h + m + 114) % 31

    jour = p + 1

    mois = n

    easter = set_dtime(y, mois, jour, tz_utc)
    easter_monday = dtime_add_days(easter, 1)
    ascension_day = dtime_add_days(easter, 39)
    pentecost = dtime_add_days(easter_monday, 49)

    return [easter, easter_monday, ascension_day, pentecost]


def jours_feries(y: int = None) -> list[datetime]:
    """
    Renvoie la liste des jours fériés pour l'année spécifiée.

    Inclut les jours fixes et les fêtes mobiles calculées à partir de Pâques.

    :param y: année (int), défaut = année actuelle
    :return: liste de datetime timezone-aware (UTC)

    :Exemple:
        >>> jours_feries(2025)
        [datetime.datetime(2025, 4, 20, 0, 0, tzinfo=...), ..., datetime.datetime(2025, 12, 25, 0, 0, tzinfo=...)]
    """
    list_jours_feries = nap_days_dc[f'{y}']
    if not list_jours_feries:
        y = get_now_dtime().year if y is None else int(y)

        list_jours_feries: list = paques(y)
        # jour de lan, fete du travail, jour victoire, fete national; assomption, tousain, armistice, noël
        l_dte = ((1, 1), (5, 1), (5, 8), (7, 14), (8, 15), (10, 1), (11, 1), (12, 25))

        for month, day in l_dte:
            list_jours_feries.append(set_dtime(y, month, day, tz_utc))
        nap_days_dc[f'{y}'] = list_jours_feries

    return list_jours_feries


def is_workday(dtime):
    """
    Détermine si une date est un jour ouvré (ni week-end ni jour férié).

    :param dtime: datetime à tester
    :return: True si jour ouvré, False sinon

    :Exemple:
        >>> is_workday(datetime(2025, 5, 1))
        False  # Fête du travail
        >>> is_workday(datetime(2025, 5, 2))
        True
    """
    feries = jours_feries(dtime.year)
    return not (dtime.weekday() in [I_SAT, I_SUN] or dtime in feries)


def dtime_add_days(dtime: datetime, nb: int = 1) -> datetime:
    """
    Ajoute un nombre de jours à un datetime.

    :param dtime: datetime de départ
    :param nb: nombre de jours à ajouter (positif ou négatif)
    :return: datetime ajusté

    :Exemple:
        >>> dtime_add_days(datetime(2025,1,1), 2)
        datetime.datetime(2025, 1, 3, 0, 0)
    """
    return dtime + timedelta(days=nb)


def dtime_add_hours(dtime: datetime, nb: int = 1) -> datetime:
    """
    Ajoute un nombre d'heures à un datetime.

    :param dtime: datetime de départ
    :param nb: nombre d'heures à ajouter
    :return: datetime ajusté
    """
    return dtime + timedelta(hours=nb)


def dtime_add_minutes(dtime: datetime, nb: int = 1) -> datetime:
    """
    Ajoute un nombre de minutes à un datetime.

    :param dtime: datetime de départ
    :param nb: nombre de minutes à ajouter
    :return: datetime ajusté
    """
    return dtime + timedelta(minutes=nb)


def dte_add_workday(dtime, nb):
    """
    Ajoute un nombre de jours ouvrés à une date.

    Incrémente la date en sautant week-ends et jours fériés.

    :param dtime: date de départ (datetime)
    :param nb: nombre de jours ouvrés à ajouter (positif)
    :return: datetime ajusté

    :Exemple:
        >>> dte_add_workday(datetime(2025,5,1), 3)
        datetime.datetime(2025, 5, 7, 0, 0)  # en sautant le 1er mai et le weekend
    """
    while nb > 0:
        dtime = dtime_add_days(dtime, 1)
        if is_workday(dtime):
            nb -= 1

    return dtime


def dtime_diff(dtea: datetime, dteb: datetime):
    """
    Calcule la différence en jours entre deux dates.

    :param dtea: première date
    :param dteb: deuxième date
    :return: différence absolue en jours (int)

    :Exemple:
        >>> dtime_diff(datetime(2025,1,1), datetime(2025,1,10))
        9
    """
    t = dteb - dtea
    return abs(t.days)


def dtime_compare(dtea: datetime, dteb: datetime):
    """
    Compare deux dates.

    :param dtea: première date
    :param dteb: deuxième date
    :return: 0 si égales, -1 si dteb < dtea, 1 sinon

    :Exemple:
        >>> dtime_compare(datetime(2025,1,1), datetime(2025,1,1))
        0
        >>> dtime_compare(datetime(2025,1,2), datetime(2025,1,1))
        -1
    """
    t = dteb - dtea

    if t.days == 0:
        return t.days
    elif t.days < 0:
        return -1
    else:
        return 1


def weeks_num(dtime: datetime | date | None = None):
    """
    Renvoie le numéro ISO de la semaine pour une date donnée (ou aujourd'hui par défaut).

    :param dtime: date ou datetime ou None
    :return: numéro de semaine (int)

    :Exemple:
        >>> weeks_num(datetime(2025,1,1))
        1
    """
    if dtime is None:
        dtime = get_now_dtime()
    else:
        dtime = dte_to_dtime(dtime)

    return dtime.isocalendar()[1]


def dtime_month_str(dtime):
    """
    Renvoie le mois et l'année d'une date sous forme de chaîne.

    :param dtime: datetime
    :return: chaîne formatée "Mois YYYY"

    :Exemple:
        >>> dtime_month_str(datetime(2025,1,15))
        'janvier 2025'
    """
    dtime = dte_to_dtime(dtime)
    return get_dtime_str(dtime, "%B %Y")


def month_to_fullmonth(month: int, year: None = None) -> str:
    """
    Renvoie le mois et l'année d'une date sous forme de chaîne.

    :param year:
    :param month:
    :return: chaîne formatée "Mois YYYY"

    :Exemple:
        >>> dtime_month_str(datetime(2025,1,15))
        'janvier 2025'
    """
    if year:
        year = get_now_dtime().year

    dte = set_dte(year, month, 1)
    return dtime_month_str(dte)


def dtime_rss_str(dtime=None, short=False):
    """
    Renvoie une date au format RSS.

    :param dtime: datetime ou None (aujourd'hui)
    :param short: bool, si True format court, sinon format complet
    :return: chaîne formatée

    :Exemple:
        >>> dtime_rss_str(datetime(2025,1,1), short=True)
        'Wed 01 Jan 2025'
    """
    dtime = dte_to_dtime(dtime)
    return get_dtime_str(dtime, fm=FR_FORMAT_RSS_SHORT) if short else get_dtime_str(dtime, fm=FR_FORMAT_RSS_2)


def day_in_hour(nb_day: int) -> int:
    """
    Convertit un nombre de jours en heures.

    :param nb_day: nombre de jours
    :return: nombre d'heures

    :Exemple:
        >>> day_in_hour(2)
        48
    """
    return nb_day * 24


def day_in_minutes(nb_day: int) -> int:
    """
    Convertit un nombre de jours en minutes.

    :param nb_day: nombre de jours
    :return: nombre de minutes

    :Exemple:
        >>> day_in_minutes(2)
        2880
    """
    return day_in_hour(nb_day) * 60


def day_in_sec(nb_day: int) -> int:
    """
    Convertit un nombre de jours en secondes.

    :param nb_day: nombre de jours
    :return: nombre de secondes

    :Exemple:
        >>> day_in_sec(1)
        86400
    """
    return day_in_minutes(nb_day) * 60


def current_year():
    # Test de la permission kozman_moderator
    return get_today_str(fm="%Y")


def day_in_msec(nb_day: int) -> int:
    """
    Convertit un nombre de jours en millisecondes.

    :param nb_day: nombre de jours
    :return: nombre de millisecondes

    :Exemple:
        >>> day_in_msec(1)
        86400000
    """
    return day_in_sec(nb_day) * 1000

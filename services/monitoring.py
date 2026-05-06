# services/monitoring.py

from database.system_map import get_all_latest_data


def get_monitoring_data():
    """
    Get latest UF + RO monitoring data for dashboard
    """

    # Read all sensors using system map
    data = get_all_latest_data()

    return data

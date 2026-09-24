def get_active_window_title() -> str:
    try:
        from Xlib import display, X
        d = display.Display()
        root = d.screen().root
        active_prop = root.get_full_property(
            d.intern_atom('_NET_ACTIVE_WINDOW'), X.AnyPropertyType
        )
        if not active_prop:
            return ""
        win_id = active_prop.value[0]
        window = d.create_resource_object('window', win_id)
        name_prop = window.get_full_property(
            d.intern_atom('_NET_WM_NAME'), X.AnyPropertyType
        )
        if name_prop:
            return name_prop.value.decode('utf-8', errors='replace')
        # fallback to WM_NAME
        name_prop2 = window.get_full_property(
            d.intern_atom('WM_NAME'), X.AnyPropertyType
        )
        return name_prop2.value.decode('latin-1', errors='replace') if name_prop2 else ""
    except Exception:
        return ""

"""
Flagged Words nedir?

  Belgede bu kelimelerin oranı belirlenen eşiğin üzerindeyse belge atılır.
  Stopword filtresinin tersidir: bu kelimeler çok geçiyorsa belge uygunsuz
  içerik (pornografi, ağır argo, spam) barındırıyor demektir.

  Parametredeki karşılığı:
    "flagged_words_max_cutoff": 0.05  # kelimelerin en fazla %5'i flagged olabilir
"""

flagged_words_tr = [
    # --- Cinsel içerikli argo ---
    "am", "amcık", "amına", "amını", "amınakoyayım",
    "göt", "götü", "götüne", "götlek",
    "orospu", "orospuçocuğu", "fahişe", "seks",
    "sikiş", "sikişmek", "sikmek", "siktir",
    "siktim", "sikeyim", "sikici",
    "yarrak", "yarak", "yarrağı", "yarrağına",
    "taşak", "dalyarak",
    "ospu", "orospu",
    "porno", "pornografi", "pornosu",
    "pik", "piç", "piçlik",
    "döl", "meni",
    "vajina", "penis", "seks",
    "escort", "masaj salonu",
    "erotik", "erotizm",
    "hentai", "japon porno",
    "anal", "oral seks", "sakso",
    "ibne", "ibnelik",
    "götveren", "göt veren",

    # --- Hakaret / nefret söylemi ---
    "aptal", "salak", "gerizekalı", "geri zekalı",
    "dangalak", "ahmak", "eşek",
    "mal", "malık",
    "bok", "boktan", "boku",
    "it", "köpek", "köpeğin",
    "hıyar", "götveren",
    "embesil", "budala",
    "oç", "oçluk",
    "şerefsiz", "şerefsizlik",
    "namussuz", "namussuzluk",
    "alçak", "alçaklık",
    "kahpe", "kahpelik",
    "kaltak", "kaltaklık",
    "sürtük",
    "pezevenk", "pezevenklik",
    "bok yemek", "bok yedin",

    # --- Irkçı / ayrımcı ifadeler ---
    "zenci", "zenciler",
    "çingene", "çingeneler",
    "gavur", "gavurlar",
    "kâfir", "kafir",

    # --- Şiddet içerikli argo ---
    "öldüreceğim", "gebertmek", "geberteyim",

    # --- Kumar / yasadışı içerik ---
    "kumar", "casinoda", "bahis sitesi",
    "illegal", "kaçakçı", "uyuşturucu satış",
    "eroin", "kokain", "uyuşturucu", "esrar", "bonzai",
    "lsd"
]

flagged_words_tr = list(set(flagged_words_tr))

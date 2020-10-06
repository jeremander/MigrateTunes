import setuptools

setuptools.setup(
    name = "migratetunes",
    version = "0.0.1",
    author = "Jeremy Silver",
    author_email = "jsilver9887@gmail.com",
    description = "Converts iTunes library to Rhythmbox.",
    url = "https://github.com/jeremander/MigrateTunes",
    packages = setuptools.find_packages(),
    entry_points = {
        'console_scripts': [
            'migrate-playlists = migratetunes.migrate_playlists:main',
            'integrate-song-info = migratetunes.integrate_song_info:main'
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)
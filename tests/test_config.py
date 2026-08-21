from chatenv import BaseEnvConfig, EnvStore

from chatrss.config import ChatRssConfig


def test_chatrss_config_is_typed_and_marks_document_token_sensitive():
    assert issubclass(ChatRssConfig, BaseEnvConfig)
    assert ChatRssConfig._aliases == ["chatrss", "rss"]
    assert ChatRssConfig.get_storage_name() == "ChatRss"

    fields = ChatRssConfig.get_fields()
    assert fields["CHATRSS_LARK_DOC_TOKEN"].is_sensitive is True
    assert fields["CHATRSS_DEFAULT_REPO"].is_sensitive is False


def test_chatrss_profiles_use_chatenv_storage_paths(tmp_path):
    envs_dir = tmp_path / "envs"
    store = EnvStore(envs_dir)
    values = {
        "CHATRSS_DEFAULT_REPO": "ChatArch/ChatRSS",
        "CHATRSS_RSSHUB_URL": "https://rsshub.example.invalid",
    }

    profile_path = store.save_profile(ChatRssConfig, "work", values)

    assert profile_path == ChatRssConfig.get_profile_env_file(envs_dir, "work")
    assert profile_path == envs_dir / "ChatRss" / "work.env"
    assert store.load_profile(ChatRssConfig, "work") == values

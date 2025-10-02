from __future__ import annotations

from dataclasses import dataclass, asdict


@dataclass
class ModulePaths:
    """
    Module and path references for Python imports.

    Example:
        module: 'app.human_resource.employee.skill'
        module_path: 'app.human_resource.employee.skill'

    """

    module: str
    module_path: str


@dataclass
class ModelNames:
    """
    Model class and instance naming conventions.

    Example:
        model_class_name: 'EmployeeSkill'
        model_class_name_plural: 'EmployeeSkills'
        model_instance_name: 'employee_skill'
        model_instance_name_plural: 'employee_skills'
        model_verbose_name: 'Employee Skill'
        model_verbose_name_plural: 'Employee Skills'

    """

    model_class_name: str
    model_class_name_plural: str
    model_instance_name: str
    model_instance_name_plural: str
    model_verbose_name: str
    model_verbose_name_plural: str


@dataclass
class ModelPermissions:
    """
    MODEL_PERMISSIONS configuration for apps.py.

    Example:
        permission_name: 'employee_skill'
        model_class_path: 'app.human_resource.employee.skill.models.EmployeeSkill'
        is_proxy_model: 'False'
        is_proxy_model_bool: False

    """

    permission_name: str
    model_class_path: str
    is_proxy_model: str
    is_proxy_model_bool: bool


@dataclass
class AppConfiguration:
    """
    Django app configuration and labeling.

    Example:
        app_config_class_name: 'EmployeeSkillConfig'
        app_name_component: 'skill'
        django_label: 'employee_skill'
        permission_prefix: 'employee_skill'
        db_table_name: 'employee_skill'

    """

    app_config_class_name: str
    app_name_component: str
    django_label: str
    permission_prefix: str
    db_table_name: str


@dataclass
class ParentReferences:
    """
    Parent app and model references.

    Example:
        parent_app_name: 'employee'
        parent_model_class_name: 'Employee'

    """

    parent_app_name: str
    parent_model_class_name: str


@dataclass
class ServiceClasses:
    """
    Service layer class names.

    Example:
        service_class_name: 'EmployeeSkillService'
        factory_service_class_name: 'EmployeeSkillFactoryService'
        intelligence_service_class_name: 'EmployeeSkillIntelligenceService'
        processor_service_class_name: 'EmployeeSkillProcessorService'
        transformation_service_class_name: 'EmployeeSkillTransformationService'

    """

    service_class_name: str
    factory_service_class_name: str
    intelligence_service_class_name: str
    processor_service_class_name: str
    transformation_service_class_name: str


@dataclass
class IntelligenceClasses:
    """
    LLM/AI related class names.

    Example:
        bot_class_name: 'EmployeeSkillBot'
        intel_class_name: 'EmployeeSkillIntel'

    """

    bot_class_name: str
    intel_class_name: str


@dataclass
class DataClasses:
    """
    Data layer class names (seeders, querysets, forms).

    Example:
        seeder_class_name: 'EmployeeSkillSeeder'
        queryset_class_name: 'EmployeeSkillQuerySet'
        form_class_name: 'EmployeeSkillForm'

    """

    seeder_class_name: str
    queryset_class_name: str
    form_class_name: str


@dataclass
class TestClasses:
    """
    Test case class names.

    Example:
        model_test_class_name: 'EmployeeSkillModelTestCase'
        bot_test_class_name: 'EmployeeSkillBotTestCase'
        service_test_class_name: 'EmployeeSkillServiceTestCase'
        factory_service_test_class_name: 'EmployeeSkillFactoryServiceTestCase'
        intelligence_service_test_class_name: 'EmployeeSkillIntelligenceServiceTestCase'
        processor_service_test_class_name: 'EmployeeSkillProcessorServiceTestCase'
        transformation_service_test_class_name: 'EmployeeSkillTransformationServiceTestCase'
        url_test_class_name: 'EmployeeSkillUrlTestCase'
        view_test_class_name: 'EmployeeSkillViewTestCase'

    """

    model_test_class_name: str
    bot_test_class_name: str
    service_test_class_name: str
    factory_service_test_class_name: str
    intelligence_service_test_class_name: str
    processor_service_test_class_name: str
    transformation_service_test_class_name: str
    url_test_class_name: str
    view_test_class_name: str


@dataclass
class URLPatterns:
    """
    URL routing and namespaces.

    Example:
        url_namespace: 'skill'
        url_reverse_path: 'employee:skill'
        url_reverse_parent_path: 'employee'

    """

    url_namespace: str
    url_reverse_path: str
    url_reverse_parent_path: str


@dataclass
class TemplatePaths:
    """
    Template file paths and names.

    Example:
        template_directory_path: 'employee/skill'
        detail_card_template_name: 'employee_skill_detail_card.html'
        form_card_template_name: 'employee_skill_form_card.html'
        list_card_template_name: 'employee_skill_list_card.html'
        item_template_name: 'employee_skill_item.html'
        form_template_name: 'employee_skill_form.html'
        detail_page_template_name: 'employee_skill_detail_page.html'
        form_page_template_name: 'employee_skill_form_page.html'
        list_page_template_name: 'employee_skill_list_page.html'

    """

    template_directory_path: str
    detail_card_template_name: str
    form_card_template_name: str
    list_card_template_name: str
    item_template_name: str
    form_template_name: str
    detail_page_template_name: str
    form_page_template_name: str
    list_page_template_name: str


@dataclass
class PromptFunctions:
    """
    LLM prompt function names.

    Example:
        instruction_prompt_function_name: 'employee_skill_instruction_prompt'
        user_input_prompt_function_name: 'employee_skill_user_input_prompt'

    """

    instruction_prompt_function_name: str
    user_input_prompt_function_name: str


@dataclass
class ViewFunctions:
    """
    View function names.

    Example:
        list_page_view_name: 'list_page_view'
        detail_page_view_name: 'detail_page_view'
        create_form_view_name: 'create_form_view'
        update_form_view_name: 'update_form_view'
        delete_form_view_name: 'delete_form_view'
        create_modal_form_view_name: 'create_modal_form_view'
        update_modal_form_view_name: 'update_modal_form_view'
        delete_modal_form_view_name: 'delete_modal_form_view'

    """

    list_page_view_name: str
    detail_page_view_name: str
    create_form_view_name: str
    update_form_view_name: str
    delete_form_view_name: str
    create_modal_form_view_name: str
    update_modal_form_view_name: str
    delete_modal_form_view_name: str


@dataclass
class ContextVariables:
    """
    Template context variable names and django_glue keys.

    Example:
        glue_model_key: 'employee_skill'
        context_single_var: 'employee_skill'
        context_plural_var: 'employee_skills'

    """

    glue_model_key: str
    context_single_var: str
    context_plural_var: str


def generate_replacement_map(
    components: list[str],
    user_inputs: dict[str, str] | None = None
) -> dict[str, str]:
    """Generate replacement mappings for template processing."""

    if user_inputs:
        app_name = user_inputs.get('app_name', components[-1])
        model_name = user_inputs.get('model_name')
        model_name_plural = user_inputs.get('model_name_plural')
        app_label = user_inputs.get('app_label')
        db_table_name = user_inputs.get('db_table_name')
        model_permission_path = user_inputs.get('model_permission_path')
        verbose_name = user_inputs.get('verbose_name')
        verbose_name_plural = user_inputs.get('verbose_name_plural')
        is_proxy_model = user_inputs.get('is_proxy_model', False)
    else:
        app_name = components[-1]
        model_name = None
        model_name_plural = None
        app_label = None
        db_table_name = None
        model_permission_path = None
        verbose_name = None
        verbose_name_plural = None
        is_proxy_model = False

    if len(components) > 1:
        parents = components[0:-1]
        parent = components[-2]
    else:
        parents = [app_name]
        parent = app_name

    module = '.'.join(components)
    parent_parts = parents[1:]
    is_root = len(parent_parts) == 0

    if is_root:
        reverse_parent_path = ''
        reverse_path = app_name.lower()
        default_label_path = app_name.lower()
        template_path = app_name.lower()
        default_permission_name = app_name.lower()
    else:
        reverse_parent_path = ':'.join(parent_parts).lower()
        reverse_path = ':'.join(parent_parts).lower() + ':' + app_name.lower()
        default_label_path = '_'.join(parent_parts).lower() + '_' + app_name.lower()
        template_path = '/'.join(parent_parts).lower() + '/' + app_name.lower()
        default_permission_name = default_label_path

    default_model_name = ''.join(word.title() for word in app_name.split('_'))
    final_model_name = model_name if model_name else default_model_name
    final_model_name_plural = model_name_plural if model_name_plural else final_model_name + 's'

    default_verbose_name = ' '.join(word.title() for word in app_name.split('_'))
    final_verbose_name = verbose_name if verbose_name else default_verbose_name
    final_verbose_name_plural = verbose_name_plural if verbose_name_plural else final_verbose_name + 's'

    final_app_label = app_label if app_label else default_label_path
    final_db_table = db_table_name if db_table_name else default_label_path
    final_permission_path = model_permission_path if model_permission_path else f'{module}.models.{final_model_name}'
    final_permission_name = default_permission_name

    module_paths = ModulePaths(
        module=module,
        module_path=module,
    )

    model_names = ModelNames(
        model_class_name=final_model_name,
        model_class_name_plural=final_model_name_plural,
        model_instance_name=app_name.lower(),
        model_instance_name_plural=app_name.lower() + 's',
        model_verbose_name=final_verbose_name,
        model_verbose_name_plural=final_verbose_name_plural,
    )

    model_permissions = ModelPermissions(
        permission_name=final_permission_name,
        model_class_path=final_permission_path,
        is_proxy_model=str(is_proxy_model),
        is_proxy_model_bool=is_proxy_model,
    )

    app_config = AppConfiguration(
        app_config_class_name=final_model_name + 'Config',
        app_name_component=app_name,
        django_label=final_app_label,
        permission_prefix=final_app_label,
        db_table_name=final_db_table,
    )

    parent_refs = ParentReferences(
        parent_app_name=parent.lower(),
        parent_model_class_name=''.join(word.title() for word in parent.split('_')),
    )

    services = ServiceClasses(
        service_class_name=final_model_name + 'Service',
        factory_service_class_name=final_model_name + 'FactoryService',
        intelligence_service_class_name=final_model_name + 'IntelligenceService',
        processor_service_class_name=final_model_name + 'ProcessorService',
        transformation_service_class_name=final_model_name + 'TransformationService',
    )

    intelligence = IntelligenceClasses(
        bot_class_name=final_model_name + 'Bot',
        intel_class_name=final_model_name + 'Intel',
    )

    data_classes = DataClasses(
        seeder_class_name=final_model_name + 'Seeder',
        queryset_class_name=final_model_name + 'QuerySet',
        form_class_name=final_model_name + 'Form',
    )

    tests = TestClasses(
        model_test_class_name=final_model_name + 'ModelTestCase',
        bot_test_class_name=final_model_name + 'BotTestCase',
        service_test_class_name=final_model_name + 'ServiceTestCase',
        factory_service_test_class_name=final_model_name + 'FactoryServiceTestCase',
        intelligence_service_test_class_name=final_model_name + 'IntelligenceServiceTestCase',
        processor_service_test_class_name=final_model_name + 'ProcessorServiceTestCase',
        transformation_service_test_class_name=final_model_name + 'TransformationServiceTestCase',
        url_test_class_name=final_model_name + 'UrlTestCase',
        view_test_class_name=final_model_name + 'ViewTestCase',
    )

    urls = URLPatterns(
        url_namespace=app_name.lower(),
        url_reverse_path=reverse_path,
        url_reverse_parent_path=reverse_parent_path,
    )

    templates = TemplatePaths(
        template_directory_path=template_path,
        detail_card_template_name=app_name.lower() + '_detail_card',
        form_card_template_name=app_name.lower() + '_form_card',
        list_card_template_name=app_name.lower() + '_list_card',
        item_template_name=app_name.lower() + '_item',
        form_template_name=app_name.lower() + '_form',
        detail_page_template_name=app_name.lower() + '_detail_page',
        form_page_template_name=app_name.lower() + '_form_page',
        list_page_template_name=app_name.lower() + '_list_page',
    )

    prompts = PromptFunctions(
        instruction_prompt_function_name=app_name.lower() + '_instruction_prompt',
        user_input_prompt_function_name=app_name.lower() + '_user_input_prompt',
    )

    views = ViewFunctions(
        list_page_view_name='list_page_view',
        detail_page_view_name='detail_page_view',
        create_form_view_name='create_form_view',
        update_form_view_name='update_form_view',
        delete_form_view_name='delete_form_view',
        create_modal_form_view_name='create_modal_form_view',
        update_modal_form_view_name='update_modal_form_view',
        delete_modal_form_view_name='delete_modal_form_view',
    )

    context = ContextVariables(
        glue_model_key=app_name.lower(),
        context_single_var=app_name.lower(),
        context_plural_var=app_name.lower() + 's',
    )

    return {
        **asdict(module_paths),
        **asdict(model_names),
        **{
            k: v
            for k, v in asdict(model_permissions).items()
            if k != 'is_proxy_model_bool'
        },
        **asdict(app_config),
        **asdict(parent_refs),
        **asdict(services),
        **asdict(intelligence),
        **asdict(data_classes),
        **asdict(tests),
        **asdict(urls),
        **asdict(templates),
        **asdict(prompts),
        **asdict(views),
        **asdict(context),
    }

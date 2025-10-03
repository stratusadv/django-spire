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

    @classmethod
    def build(cls, components: list[str], **_kwargs) -> ModulePaths:
        module = '.'.join(components)
        return cls(module=module, module_path=module)


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

    @classmethod
    def build(
        cls,
        components: list[str],
        user_inputs: dict[str, str] | None = None
    ) -> ModelNames:
        app_name = (
            user_inputs.get('app_name', components[-1])
            if user_inputs
            else components[-1]
        )

        default_model_name = ''.join(
            word.title()
            for word in app_name.split('_')
        )

        model_name = (
            user_inputs.get('model_name', default_model_name)
            if user_inputs
            else default_model_name
        )

        model_name_plural = (
            user_inputs.get('model_name_plural', model_name + 's')
            if user_inputs
            else model_name + 's'
        )

        default_verbose_name = ' '.join(
            word.title()
            for word in app_name.split('_')
        )

        verbose_name = (
            user_inputs.get('verbose_name', default_verbose_name)
            if user_inputs
            else default_verbose_name
        )

        verbose_name_plural = (
            user_inputs.get('verbose_name_plural', verbose_name + 's')
            if user_inputs
            else verbose_name + 's'
        )

        return cls(
            model_class_name=model_name,
            model_class_name_plural=model_name_plural,
            model_instance_name=app_name.lower(),
            model_instance_name_plural=app_name.lower() + 's',
            model_verbose_name=verbose_name,
            model_verbose_name_plural=verbose_name_plural,
        )


@dataclass
class ModelPermissions:
    """
    MODEL_PERMISSIONS configuration for apps.py.

    Example:
        permission_name: 'employee_skill'
        model_class_path: 'app.human_resource.employee.skill.models.EmployeeSkill'

    """

    permission_name: str
    model_class_path: str

    @classmethod
    def build(
        cls,
        components: list[str],
        user_inputs: dict[str, str] | None = None
    ) -> ModelPermissions:
        module = '.'.join(components)
        parent_parts = components[1:-1] if len(components) > 1 else []

        app_name = (
            user_inputs.get('app_name', components[-1])
            if user_inputs
            else components[-1]
        )

        default_model_name = ''.join(
            word.title()
            for word in app_name.split('_')
        )

        model_name = (
            user_inputs.get('model_name', default_model_name)
            if user_inputs
            else default_model_name
        )

        default_permission_name = (
            '_'.join(parent_parts).lower() + '_' + app_name.lower()
            if parent_parts
            else app_name.lower()
        )

        permission_path = (
            user_inputs.get('model_permission_path', f'{module}.models.{model_name}')
            if user_inputs
            else f'{module}.models.{model_name}'
        )

        return cls(
            permission_name=default_permission_name,
            model_class_path=permission_path,
        )


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

    @classmethod
    def build(
        cls,
        components: list[str],
        user_inputs: dict[str, str] | None = None
    ) -> AppConfiguration:
        parent_parts = components[1:-1] if len(components) > 1 else []

        app_name = (
            user_inputs.get('app_name', components[-1])
            if user_inputs
            else components[-1]
        )

        default_model_name = ''.join(
            word.title()
            for word in app_name.split('_')
        )

        model_name = (
            user_inputs.get('model_name', default_model_name)
            if user_inputs
            else default_model_name
        )

        default_label = (
            '_'.join(parent_parts).lower() + '_' + app_name.lower()
            if parent_parts
            else app_name.lower()
        )

        app_label = (
            user_inputs.get('app_label', default_label)
            if user_inputs
            else default_label
        )

        db_table = (
            user_inputs.get('db_table_name', default_label)
            if user_inputs
            else default_label
        )

        return cls(
            app_config_class_name=model_name + 'Config',
            app_name_component=app_name,
            django_label=app_label,
            permission_prefix=app_label,
            db_table_name=db_table,
        )


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

    @classmethod
    def build(cls, components: list[str], **_kwargs) -> ParentReferences:
        parent = components[-2] if len(components) > 1 else components[-1]

        return cls(
            parent_app_name=parent.lower(),
            parent_model_class_name=''.join(
                word.title()
                for word in parent.split('_')
            ),
        )


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

    @classmethod
    def build(
        cls,
        components: list[str],
        user_inputs: dict[str, str] | None = None
    ) -> ServiceClasses:
        app_name = (
            user_inputs.get('app_name', components[-1])
            if user_inputs
            else components[-1]
        )

        default_model_name = ''.join(
            word.title()
            for word in app_name.split('_')
        )

        model_name = (
            user_inputs.get('model_name', default_model_name)
            if user_inputs
            else default_model_name
        )

        return cls(
            service_class_name=model_name + 'Service',
            factory_service_class_name=model_name + 'FactoryService',
            intelligence_service_class_name=model_name + 'IntelligenceService',
            processor_service_class_name=model_name + 'ProcessorService',
            transformation_service_class_name=model_name + 'TransformationService',
        )


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

    @classmethod
    def build(
        cls,
        components: list[str],
        user_inputs: dict[str, str] | None = None
    ) -> IntelligenceClasses:
        app_name = (
            user_inputs.get('app_name', components[-1])
            if user_inputs
            else components[-1]
        )

        default_model_name = ''.join(
            word.title()
            for word in app_name.split('_')
        )

        model_name = (
            user_inputs.get('model_name', default_model_name)
            if user_inputs
            else default_model_name
        )

        return cls(
            bot_class_name=model_name + 'Bot',
            intel_class_name=model_name + 'Intel',
        )


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

    @classmethod
    def build(
        cls,
        components: list[str],
        user_inputs: dict[str, str] | None = None
    ) -> DataClasses:
        app_name = (
            user_inputs.get('app_name', components[-1])
            if user_inputs
            else components[-1]
        )

        default_model_name = ''.join(
            word.title()
            for word in app_name.split('_')
        )

        model_name = (
            user_inputs.get('model_name', default_model_name)
            if user_inputs
            else default_model_name
        )

        return cls(
            seeder_class_name=model_name + 'Seeder',
            queryset_class_name=model_name + 'QuerySet',
            form_class_name=model_name + 'Form',
        )


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

    @classmethod
    def build(
        cls,
        components: list[str],
        user_inputs: dict[str, str] | None = None
    ) -> TestClasses:
        app_name = (
            user_inputs.get('app_name', components[-1])
            if user_inputs
            else components[-1]
        )

        default_model_name = ''.join(
            word.title()
            for word in app_name.split('_')
        )

        model_name = (
            user_inputs.get('model_name', default_model_name)
            if user_inputs
            else default_model_name
        )

        return cls(
            model_test_class_name=model_name + 'ModelTestCase',
            bot_test_class_name=model_name + 'BotTestCase',
            service_test_class_name=model_name + 'ServiceTestCase',
            factory_service_test_class_name=model_name + 'FactoryServiceTestCase',
            intelligence_service_test_class_name=model_name + 'IntelligenceServiceTestCase',
            processor_service_test_class_name=model_name + 'ProcessorServiceTestCase',
            transformation_service_test_class_name=model_name + 'TransformationServiceTestCase',
            url_test_class_name=model_name + 'UrlTestCase',
            view_test_class_name=model_name + 'ViewTestCase',
        )


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

    @classmethod
    def build(
        cls,
        components: list[str],
        user_inputs: dict[str, str] | None = None
    ) -> URLPatterns:
        app_name = (
            user_inputs.get('app_name', components[-1])
            if user_inputs
            else components[-1]
        )

        parent_parts = components[1:-1] if len(components) > 1 else []

        if parent_parts:
            reverse_parent = ':'.join(parent_parts).lower()
            reverse_path = reverse_parent + ':' + app_name.lower()
        else:
            reverse_parent = ''
            reverse_path = app_name.lower()

        return cls(
            url_namespace=app_name.lower(),
            url_reverse_path=reverse_path,
            url_reverse_parent_path=reverse_parent,
        )


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

    @classmethod
    def build(
        cls,
        components: list[str],
        user_inputs: dict[str, str] | None = None
    ) -> TemplatePaths:
        app_name = (
            user_inputs.get('app_name', components[-1])
            if user_inputs
            else components[-1]
        )

        parent_parts = components[1:-1] if len(components) > 1 else []

        template_path = (
            '/'.join(parent_parts).lower() + '/' + app_name.lower()
            if parent_parts
            else app_name.lower()
        )

        return cls(
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

    @classmethod
    def build(
        cls,
        components: list[str],
        user_inputs: dict[str, str] | None = None
    ) -> PromptFunctions:
        app_name = (
            user_inputs.get('app_name', components[-1])
            if user_inputs
            else components[-1]
        )

        return cls(
            instruction_prompt_function_name=app_name.lower() + '_instruction_prompt',
            user_input_prompt_function_name=app_name.lower() + '_user_input_prompt',
        )


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

    @classmethod
    def build(cls, components: list[str], **_kwargs) -> ViewFunctions:
        return cls(
            list_page_view_name='list_page_view',
            detail_page_view_name='detail_page_view',
            create_form_view_name='create_form_view',
            update_form_view_name='update_form_view',
            delete_form_view_name='delete_form_view',
            create_modal_form_view_name='create_modal_form_view',
            update_modal_form_view_name='update_modal_form_view',
            delete_modal_form_view_name='delete_modal_form_view',
        )


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

    @classmethod
    def build(
        cls,
        components: list[str],
        user_inputs: dict[str, str] | None = None
    ) -> ContextVariables:
        app_name = (
            user_inputs.get('app_name', components[-1])
            if user_inputs
            else components[-1]
        )

        return cls(
            glue_model_key=app_name.lower(),
            context_single_var=app_name.lower(),
            context_plural_var=app_name.lower() + 's',
        )


@dataclass
class ReplacementMapBuilder:
    """Aggregates all dataclasses and builds the final replacement map."""

    module_paths: ModulePaths
    model_names: ModelNames
    model_permissions: ModelPermissions
    app_config: AppConfiguration
    parent_refs: ParentReferences
    services: ServiceClasses
    intelligence: IntelligenceClasses
    data_classes: DataClasses
    tests: TestClasses
    urls: URLPatterns
    templates: TemplatePaths
    prompts: PromptFunctions
    views: ViewFunctions
    context: ContextVariables

    @classmethod
    def build(
        cls,
        components: list[str],
        user_inputs: dict[str, str] | None = None
    ) -> ReplacementMapBuilder:
        return cls(
            module_paths=ModulePaths.build(components, user_inputs=user_inputs),
            model_names=ModelNames.build(components, user_inputs=user_inputs),
            model_permissions=ModelPermissions.build(components, user_inputs=user_inputs),
            app_config=AppConfiguration.build(components, user_inputs=user_inputs),
            parent_refs=ParentReferences.build(components, user_inputs=user_inputs),
            services=ServiceClasses.build(components, user_inputs=user_inputs),
            intelligence=IntelligenceClasses.build(components, user_inputs=user_inputs),
            data_classes=DataClasses.build(components, user_inputs=user_inputs),
            tests=TestClasses.build(components, user_inputs=user_inputs),
            urls=URLPatterns.build(components, user_inputs=user_inputs),
            templates=TemplatePaths.build(components, user_inputs=user_inputs),
            prompts=PromptFunctions.build(components, user_inputs=user_inputs),
            views=ViewFunctions.build(components, user_inputs=user_inputs),
            context=ContextVariables.build(components, user_inputs=user_inputs),
        )

    def to_dict(self) -> dict[str, str]:
        """Convert the builder to a flat dictionary for template replacement."""

        return {
            **asdict(self.module_paths),
            **asdict(self.model_names),
            **asdict(self.model_permissions),
            **asdict(self.app_config),
            **asdict(self.parent_refs),
            **asdict(self.services),
            **asdict(self.intelligence),
            **asdict(self.data_classes),
            **asdict(self.tests),
            **asdict(self.urls),
            **asdict(self.templates),
            **asdict(self.prompts),
            **asdict(self.views),
            **asdict(self.context),
        }


def generate_replacement_map(
    components: list[str],
    user_inputs: dict[str, str] | None = None
) -> dict[str, str]:
    """Generate replacement mappings for template processing."""

    builder = ReplacementMapBuilder.build(components, user_inputs)
    return builder.to_dict()

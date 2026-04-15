"""Seed sample data for local development (teaching operations post-course only)."""
from datetime import date, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.asset import Asset
from app.models.chat_record import ChatRecord
from app.models.follow_up import FollowUp
from app.models.profile import Profile
from app.models.student import Student


def seed_data(db: Session) -> None:
    """Initialize Phase-1 seed data.

    Includes:
    - 3 students
    - each student 1 profile
    - each student 2 chat records
    - >=2 follow-up records
    - >=5 assets
    """
    # Prevent duplicate seed
    has_student = db.scalar(select(Student.id).limit(1))
    if has_student:
        return

    students = [
        Student(
            name="张三",
            wechat="zhangsan_01",
            phone="13800000001",
            course_name="短视频运营训练营",
            class_name="2026春季1班",
            graduation_date=date.today() - timedelta(days=30),
            current_direction="内容增长",
            current_stage="高意向",
            intent_level="高",
            owner="运营A",
            last_interaction_at=datetime.utcnow() - timedelta(days=1),
            next_follow_time=datetime.utcnow() + timedelta(days=1),
            remark="结课后关注副业变现",
        ),
        Student(
            name="李四",
            wechat="lisi_02",
            phone="13800000002",
            course_name="新媒体运营实战班",
            class_name="2026春季2班",
            graduation_date=date.today() - timedelta(days=20),
            current_direction="私域运营",
            current_stage="已联系",
            intent_level="中",
            owner="运营B",
            last_interaction_at=datetime.utcnow() - timedelta(days=3),
            next_follow_time=datetime.utcnow() - timedelta(hours=2),
            remark="学习信心一般，需要分层引导",
        ),
        Student(
            name="王五",
            wechat="wangwu_03",
            phone="13800000003",
            course_name="AI工具提效营",
            class_name="2026春季3班",
            graduation_date=date.today() - timedelta(days=15),
            current_direction="就业提升",
            current_stage="有兴趣",
            intent_level="中",
            owner="运营A",
            last_interaction_at=datetime.utcnow() - timedelta(days=2),
            next_follow_time=datetime.utcnow() + timedelta(days=2),
            remark="对进阶课程有兴趣，关注课程节奏",
        ),
    ]
    db.add_all(students)
    db.flush()

    db.add_all(
        [
            Profile(
                student_id=students[0].id,
                user_type="在职提升",
                main_goal="通过副业提升收入",
                main_concerns="担心课程与工作时间冲突",
                interest_direction="AI副业导向",
                risk_tags="价格敏感",
                recommended_course="AI副业变现实战营",
                recommended_action="安排1v1评估并发送成功案例",
                summary="目标明确、行动意愿高，需快速推进",
            ),
            Profile(
                student_id=students[1].id,
                user_type="转行准备",
                main_goal="完成新媒体岗位转型",
                main_concerns="零基础怕学不会",
                interest_direction="私域运营",
                risk_tags="学习顾虑",
                recommended_course="新媒体进阶就业班",
                recommended_action="先发送零基础学习路径",
                summary="需要先建立学习信心，再推进成交",
            ),
            Profile(
                student_id=students[2].id,
                user_type="求职提升",
                main_goal="提高简历竞争力",
                main_concerns="课程是否有实战项目",
                interest_direction="AI提效",
                risk_tags="观望中",
                recommended_course="AI工具实战进阶班",
                recommended_action="邀请参加公开答疑课",
                summary="兴趣明确，需内容驱动持续跟进",
            ),
        ]
    )

    # each student two chat records
    chats = [
        ChatRecord(student_id=students[0].id, source="微信", content="老师我想做副业赚钱，课程能落地吗？"),
        ChatRecord(student_id=students[0].id, source="微信", content="如果时间不多，怎么安排学习？"),
        ChatRecord(student_id=students[1].id, source="企业微信", content="我是零基础，怕学不会。"),
        ChatRecord(student_id=students[1].id, source="企业微信", content="预算有限，价格能分期吗？"),
        ChatRecord(student_id=students[2].id, source="微信群", content="结课后想继续提升，有没有实战项目？"),
        ChatRecord(student_id=students[2].id, source="微信群", content="下期什么时候开课？我想参加。"),
    ]
    db.add_all(chats)

    # at least two follow-ups
    db.add_all(
        [
            FollowUp(
                student_id=students[0].id,
                follow_time=datetime.utcnow() - timedelta(days=1),
                follow_method="微信私聊",
                content="回访结课应用情况并沟通副业目标",
                student_feedback="希望尽快了解进阶课程",
                judgment="高意向",
                next_action="发送课程大纲与案例",
                next_follow_time=datetime.utcnow() + timedelta(days=1),
            ),
            FollowUp(
                student_id=students[1].id,
                follow_time=datetime.utcnow() - timedelta(hours=20),
                follow_method="语音沟通",
                content="针对零基础顾虑做学习路径说明",
                student_feedback="担心跟不上节奏",
                judgment="需持续培育",
                next_action="发送零基础路线图",
                next_follow_time=datetime.utcnow() + timedelta(days=2),
            ),
            FollowUp(
                student_id=students[2].id,
                follow_time=datetime.utcnow() - timedelta(hours=10),
                follow_method="微信群",
                content="答疑课邀请与项目介绍",
                student_feedback="愿意参加公开课",
                judgment="有兴趣",
                next_action="公开课后1v1沟通",
                next_follow_time=datetime.utcnow() + timedelta(days=3),
            ),
        ]
    )

    # at least five assets
    db.add_all(
        [
            Asset(
                asset_type="话术",
                title="副业导向邀约话术",
                scene="1v1私聊",
                stage="有兴趣",
                direction="AI副业导向",
                content="学员你好，结合你结课后的副业目标，给你整理了一条可落地路径...",
                description="用于副业诉求学员的首次邀约",
            ),
            Asset(
                asset_type="话术",
                title="零基础安抚话术",
                scene="私聊",
                stage="已联系",
                direction="学习顾虑",
                content="你担心学不会非常正常，我们会先从0基础路径开始...",
                description="用于学不会/零基础顾虑人群",
            ),
            Asset(
                asset_type="物料",
                title="学员案例合集",
                scene="跟进发送",
                stage="有兴趣",
                direction="转化成交",
                link="https://example.com/cases",
                description="用于证明课程可落地与结果",
            ),
            Asset(
                asset_type="SOP动作",
                title="结课后7天经营SOP",
                scene="运营执行",
                stage="刚结课",
                direction="生命周期推进",
                content="D1回访 -> D3价值提醒 -> D5案例触达 -> D7邀约沟通",
                description="结课后黄金7天标准动作",
            ),
            Asset(
                asset_type="物料",
                title="进阶课程介绍页",
                scene="转化前介绍",
                stage="高意向",
                direction="复购转化",
                link="https://example.com/advanced-course",
                description="高意向学员转化资料",
            ),
        ]
    )

    db.commit()

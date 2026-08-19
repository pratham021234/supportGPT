class EmailTemplateService:
    def get_invite_template(self, workspace_name: str, invite_link: str) -> str:
        return f"""
        <html>
            <body style="font-family: Arial, sans-serif; color: #333; line-height: 1.6; max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #4F46E5;">You've been invited to {workspace_name}!</h2>
                <p>Hello,</p>
                <p>You have been invited to join the <strong>{workspace_name}</strong> workspace on SupportGPT.</p>
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{invite_link}" style="background-color: #4F46E5; color: white; padding: 12px 24px; text-decoration: none; border-radius: 4px; font-weight: bold;">Accept Invitation</a>
                </div>
                <p>If you did not expect this invitation, you can safely ignore this email.</p>
                <hr style="border: none; border-top: 1px solid #eee; margin: 20px 0;" />
                <p style="font-size: 12px; color: #888;">SupportGPT Automation Engine</p>
            </body>
        </html>
        """
        
    def get_ticket_created_template(self, ticket_id: str, title: str, priority: str, link: str) -> str:
        return f"""
        <html>
            <body style="font-family: Arial, sans-serif; color: #333; line-height: 1.6; max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #4F46E5;">New Ticket Created</h2>
                <p>A new ticket has been generated in your workspace.</p>
                <div style="background-color: #f9fafb; border-left: 4px solid #4F46E5; padding: 15px; margin: 20px 0;">
                    <p style="margin: 0;"><strong>ID:</strong> {ticket_id}</p>
                    <p style="margin: 5px 0 0 0;"><strong>Title:</strong> {title}</p>
                    <p style="margin: 5px 0 0 0;"><strong>Priority:</strong> {priority}</p>
                </div>
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{link}" style="background-color: #4F46E5; color: white; padding: 12px 24px; text-decoration: none; border-radius: 4px; font-weight: bold;">View Ticket</a>
                </div>
                <hr style="border: none; border-top: 1px solid #eee; margin: 20px 0;" />
                <p style="font-size: 12px; color: #888;">SupportGPT Automation Engine</p>
            </body>
        </html>
        """
        
    def get_escalation_template(self, ticket_id: str, title: str, reason: str, link: str) -> str:
        return f"""
        <html>
            <body style="font-family: Arial, sans-serif; color: #333; line-height: 1.6; max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #E11D48;">Ticket Escalated</h2>
                <p>A ticket has been escalated and requires immediate attention.</p>
                <div style="background-color: #fff1f2; border-left: 4px solid #E11D48; padding: 15px; margin: 20px 0;">
                    <p style="margin: 0;"><strong>ID:</strong> {ticket_id}</p>
                    <p style="margin: 5px 0 0 0;"><strong>Title:</strong> {title}</p>
                    <p style="margin: 5px 0 0 0;"><strong>Reason:</strong> {reason}</p>
                </div>
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{link}" style="background-color: #E11D48; color: white; padding: 12px 24px; text-decoration: none; border-radius: 4px; font-weight: bold;">View Escalation</a>
                </div>
                <hr style="border: none; border-top: 1px solid #eee; margin: 20px 0;" />
                <p style="font-size: 12px; color: #888;">SupportGPT Automation Engine</p>
            </body>
        </html>
        """

    def get_weekly_report_template(self, metrics: dict, link: str) -> str:
        return f"""
        <html>
            <body style="font-family: Arial, sans-serif; color: #333; line-height: 1.6; max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #4F46E5;">Weekly Support Report</h2>
                <p>Here is your weekly summary of support operations.</p>
                <div style="display: flex; gap: 10px; margin: 20px 0;">
                    <div style="background-color: #f9fafb; padding: 15px; flex: 1; text-align: center; border-radius: 4px;">
                        <div style="font-size: 24px; font-weight: bold; color: #111;">{metrics.get('total_conversations', 0)}</div>
                        <div style="font-size: 12px; color: #666;">Conversations</div>
                    </div>
                    <div style="background-color: #f9fafb; padding: 15px; flex: 1; text-align: center; border-radius: 4px;">
                        <div style="font-size: 24px; font-weight: bold; color: #10B981;">{metrics.get('ai_resolution_rate', 0)}%</div>
                        <div style="font-size: 12px; color: #666;">AI Resolution</div>
                    </div>
                </div>
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{link}" style="background-color: #4F46E5; color: white; padding: 12px 24px; text-decoration: none; border-radius: 4px; font-weight: bold;">View Full Analytics</a>
                </div>
                <hr style="border: none; border-top: 1px solid #eee; margin: 20px 0;" />
                <p style="font-size: 12px; color: #888;">SupportGPT Automation Engine</p>
            </body>
        </html>
        """

template_service = EmailTemplateService()
